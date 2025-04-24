from google_play_scraper import reviews, Sort
import sqlite3
import time
import logging

# Set up logging (like console.log with timestamps)
logging.basicConfig(
    filename='review_fetch.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def fetch_all_reviews(app_id, batch_size=100, delay=5):
    """Fetch all reviews for an app with pagination."""
    all_reviews = []
    continuation_token = None
    total_fetched = 0

    try:
        while True:
            # Fetch a batch of reviews
            result, continuation_token = reviews(
                app_id,
                lang='en',
                country='us',
                sort=Sort.NEWEST,
                count=batch_size,
                continuation_token=continuation_token
            )

            # Add fetched reviews to the list
            all_reviews.extend(result)
            total_fetched += len(result)

            # Log progress
            logging.info(f"Fetched {len(result)} reviews. Total: {total_fetched}")
            print(f"Fetched {len(result)} reviews. Total: {total_fetched}")

            # Break if no more reviews or continuation token
            if not result or continuation_token is None:
                logging.info("No more reviews to fetch.")
                break

            # Delay to avoid rate-limiting
            time.sleep(delay)

    except Exception as e:
        logging.error(f"Error fetching reviews: {e}")
        print(f"Error fetching reviews: {e}")

    return all_reviews

def save_reviews_to_db(reviews, app_id):
    """Save reviews to SQLite database in batches."""
    try:
        conn = sqlite3.connect('reviews.db')
        cursor = conn.cursor()

        # Ensure the reviews table exists
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS reviews (
                                                              review_id TEXT PRIMARY KEY,
                                                              app_id TEXT,
                                                              username TEXT,
                                                              rating INTEGER,
                                                              review_text TEXT,
                                                              date TEXT,
                                                              app_version TEXT
                       )
                       ''')

        # Insert reviews in batches
        inserted = 0
        for review in reviews:
            cursor.execute('''
                           INSERT OR IGNORE INTO reviews (review_id, app_id, username, rating, review_text, date, app_version)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                           ''', (
                               review['reviewId'],
                               app_id,
                               review.get('userName', ''),
                               review['score'],
                               review.get('content', ''),
                               review['at'].isoformat(),
                               review.get('appVersion', '')
                           ))
            inserted += 1
            # Commit every 100 reviews to optimize performance
            if inserted % 100 == 0:
                conn.commit()
                logging.info(f"Committed {inserted} reviews to database.")

        # Final commit
        conn.commit()
        logging.info(f"Saved {inserted} reviews to database.")
        print(f"Saved {inserted} reviews to database.")

    except sqlite3.Error as e:
        logging.error(f"Error saving to database: {e}")
        print(f"Error saving to database: {e}")

    finally:
        conn.close()

def verify_review_count():
    """Verify the number of reviews in the database."""
    try:
        conn = sqlite3.connect('reviews.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM reviews")
        count = cursor.fetchone()[0]
        logging.info(f"Total reviews in database: {count}")
        print(f"Total reviews in database: {count}")
        conn.close()
        return count
    except sqlite3.Error as e:
        logging.error(f"Error verifying review count: {e}")
        print(f"Error verifying review count: {e}")
        return 0

if __name__ == "__main__":
    # App ID for thetestemall.app
    app_id = "thetestemall.app"

    # Fetch all reviews (batch_size=100, delay=5 seconds)
    reviews_data = fetch_all_reviews(app_id, batch_size=100, delay=5)

    # Save reviews to database if any were fetched
    if reviews_data:
        save_reviews_to_db(reviews_data, app_id)
    else:
        logging.warning("No reviews fetched.")
        print("No reviews fetched.")

    # Verify the total number of reviews
    verify_review_count()
