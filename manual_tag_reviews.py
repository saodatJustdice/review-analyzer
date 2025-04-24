import sqlite3
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def manual_tag_reviews():
    try:
        conn = sqlite3.connect('reviews.db')
        cursor = conn.cursor()

        # Fetch reviews (limit to 10 for demo)
        cursor.execute("SELECT review_id, review_text, tags FROM reviews LIMIT 10")
        reviews = cursor.fetchall()

        for review_id, review_text, tags in reviews:
            print(f"\nReview ID: {review_id}")
            print(f"Text: {review_text}")
            print(f"Current Tags: {tags or 'None'}")
            new_tags = input("Enter new tags (comma-separated, e.g., #bug,#new): ")

            # Update tags
            if new_tags:
                current_tags = set(tags.split(',')) if tags else set()
                new_tags_set = set(new_tags.split(','))
                updated_tags = ','.join(current_tags.union(new_tags_set))
                cursor.execute('''
                               UPDATE reviews
                               SET tags = ?
                               WHERE review_id = ?
                               ''', (updated_tags, review_id))
                print(f"Updated tags: {updated_tags}")

        conn.commit()
        logging.info("Manual tagging completed.")
        print("Manual tagging completed.")

    except sqlite3.Error as e:
        logging.error(f"Error manual tagging: {e}")
        print(f"Error manual tagging: {e}")

    finally:
        conn.close()

if __name__ == "__main__":
    manual_tag_reviews()
