import sqlite3
import pandas as pd
import logging
import time
from google_play_scraper import reviews, Sort
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import spacy
import streamlit as st

# Configure logging to output to console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Output to console
    ]
)

# Load spaCy model
try:
    nlp = spacy.load('en_core_web_sm')
except Exception as e:
    logging.error(f"Error loading spaCy model: {e}")
    raise

# Tagging rules
TAG_RULES = {
    'bug': ['crash', 'bug', 'error', 'glitch', 'freeze', 'not working', 'broken'],
    'feature-request': ['add', 'wish', 'feature', 'please include', 'need', 'want'],
    'ui': ['interface', 'design', 'layout', 'look', 'navigation', 'confusing'],
    'performance': ['slow', 'lag', 'fast', 'speed', 'loading', 'delay'],
    'payment': ['payment', 'payout', 'money', 'cash', 'withdraw', 'transaction', 'paid'],
    'rewards': ['reward', 'points', 'bonus', 'earn', 'incentive', 'credit'],
    'gameplay': ['game', 'level', 'task', 'challenge', 'play', 'mission', 'quest'],
    'difficulty': ['difficult', 'hard', 'easy', 'challenging', 'tough', 'simple'],
    'fun': ['fun', 'enjoy', 'enjoyable', 'entertaining', 'awesome'],
    'scam': ['scam', 'fake', 'fraud', 'not paying', 'cheat'],
    'positive': ['great', 'awesome', 'love', 'excellent', 'amazing', 'fantastic'],
    'negative': ['bad', 'terrible', 'hate', 'awful', 'horrible', 'disappointed']
}

# Global flag to ensure init_db is called only once
_DB_INITIALIZED = False

# Initialize database table
def init_db():
    global _DB_INITIALIZED
    if _DB_INITIALIZED:
        logging.info("Database already initialized, skipping init_db.")
        return
    try:
        start_time = time.time()
        conn = sqlite3.connect('reviews.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                app_id TEXT,
                review_id TEXT PRIMARY KEY,
                username TEXT,
                date TEXT,
                rating INTEGER,
                review_text TEXT,
                sentiment TEXT,
                sentiment_score FLOAT,
                tags TEXT
            )
        ''')
        # Create an index on app_id
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_app_id ON reviews (app_id)')
        conn.commit()
        conn.close()
        _DB_INITIALIZED = True
        logging.info("Database initialized successfully.")
        logging.info(f"init_db took {time.time() - start_time:.2f} seconds")
    except Exception as e:
        logging.error(f"Error initializing database: {e}")
        raise

# Database connection (cached)
@st.cache_data
def get_reviews(app_id='cashgiraffe.app', _cache_buster=0):
    try:
        init_db()  # Ensure table exists
        start_time = time.time()
        conn = sqlite3.connect('reviews.db')
        query = "SELECT * FROM reviews WHERE app_id = ?"
        df = pd.read_sql_query(query, conn, params=(app_id,))
        conn.close()
        logging.info(f"Database query took {time.time() - start_time:.2f} seconds")

        if df.empty:
            logging.info("No reviews found in the database.")
            return pd.DataFrame()

        start_time = time.time()
        df['date'] = pd.to_datetime(df['date'])
        logging.info(f"Date conversion took {time.time() - start_time:.2f} seconds")

        start_time = time.time()
        # Optimize display_username calculation
        has_duplicates = df['username'].duplicated().any()
        if has_duplicates:
            df['display_username'] = df.apply(
                lambda x: f"{x['username']} (ID: {x['review_id'][-4:]})", axis=1)
        else:
            df['display_username'] = df['username']
        logging.info(f"Display username calculation took {time.time() - start_time:.2f} seconds")

        return df
    except Exception as e:
        logging.error(f"Error loading reviews from database: {e}")
        return pd.DataFrame()

# Function to clear the cache for get_reviews
def clear_reviews_cache():
    get_reviews.clear()

# Fetch reviews with pagination
def fetch_all_reviews(app_id, batch_size=100, delay=10, max_retries=3):
    """Fetch all reviews for an app with pagination and retry logic."""
    all_reviews = []
    continuation_token = None
    total_fetched = 0

    try:
        while True:
            retries = 0
            while retries < max_retries:
                try:
                    result, continuation_token = reviews(
                        app_id,
                        lang='en',
                        country='us',
                        sort=Sort.NEWEST,
                        count=batch_size,
                        continuation_token=continuation_token
                    )
                    all_reviews.extend(result)
                    total_fetched += len(result)
                    logging.info(f"Fetched batch of {len(result)} reviews. Total: {total_fetched}")
                    break
                except Exception as e:
                    retries += 1
                    logging.warning(f"Error fetching batch (attempt {retries}/{max_retries}): {e}")
                    if retries == max_retries:
                        logging.error(f"Max retries reached. Skipping batch.")
                        break
                    time.sleep(delay * retries)
            if not result or continuation_token is None:
                logging.info("No more reviews to fetch.")
                break
            time.sleep(delay)
    except Exception as e:
        logging.error(f"Error fetching reviews: {e}")
        return all_reviews

    return all_reviews

# Fetch reviews, analyze sentiment, and auto-tag (Step 3)
def refresh_reviews():
    try:
        logging.info("Starting review fetch...")

        app_id = 'cashgiraffe.app'

        all_reviews = fetch_all_reviews(app_id, batch_size=100, delay=10)
        logging.info("Finished fetching reviews.")

        if not all_reviews:
            return None, "No new reviews fetched."

        logging.info(f"Total reviews fetched: {len(all_reviews)}")
        logging.info(f"Sample review data (raw): {all_reviews[0] if all_reviews else 'No data'}")

        # Clean data before DataFrame conversion
        cleaned_reviews = []
        for review in all_reviews:
            try:
                def extract_value(field, default=''):
                    if isinstance(field, dict) and 'value' in field:
                        return str(field['value'])
                    return str(field) if field is not None else default

                cleaned_review = {
                    'app_id': app_id,
                    'reviewId': extract_value(review.get('reviewId', '')),
                    'userName': extract_value(review.get('userName', '')),
                    'at': review.get('at'),
                    'score': int(extract_value(review.get('score', 0), 0)) if review.get('score') is not None else 0,
                    'content': extract_value(review.get('content', ''))
                }
                for key in ['reviewId', 'userName', 'score', 'content']:
                    field = review.get(key)
                    if isinstance(field, dict):
                        logging.warning(f"Nested field found for {key}: {field}")
                    elif not isinstance(field, (str, int, type(None))):
                        logging.warning(f"Unexpected type for {key}: {field} (type: {type(field)})")
                cleaned_reviews.append(cleaned_review)
            except Exception as e:
                logging.error(f"Error processing review: {review}, Error: {e}")
                continue

        if not cleaned_reviews:
            return None, "No reviews after cleaning."

        logging.info(f"Sample review data (cleaned): {cleaned_reviews[0]}")

        # Convert to DataFrame
        logging.info("Converting to DataFrame...")
        new_reviews = pd.DataFrame(cleaned_reviews)
        logging.info("DataFrame conversion complete.")

        # Standardize column names
        new_reviews = new_reviews.rename(columns={
            'reviewId': 'review_id',
            'userName': 'username',
            'at': 'date',
            'score': 'rating',
            'content': 'review_text'
        })
        required_columns = ['app_id', 'review_id', 'username', 'date', 'rating', 'review_text']
        new_reviews = new_reviews[required_columns]

        # Add sentiment and tags columns
        new_reviews['sentiment'] = None
        new_reviews['sentiment_score'] = None
        new_reviews['tags'] = None

        # Sentiment analysis
        logging.info("Analyzing sentiment...")
        analyzer = SentimentIntensityAnalyzer()
        for idx, row in new_reviews.iterrows():
            try:
                if row['review_text']:
                    score = analyzer.polarity_scores(row['review_text'])
                    compound = score['compound']
                    new_reviews.at[idx, 'sentiment_score'] = compound
                    if compound >= 0.05:
                        new_reviews.at[idx, 'sentiment'] = 'Positive'
                    elif compound <= -0.05:
                        new_reviews.at[idx, 'sentiment'] = 'Negative'
                    else:
                        new_reviews.at[idx, 'sentiment'] = 'Neutral'
                else:
                    new_reviews.at[idx, 'sentiment'] = 'Neutral'
                    new_reviews.at[idx, 'sentiment_score'] = 0.0
            except Exception as e:
                logging.error(f"Error analyzing sentiment for review {idx}: {e}")
                new_reviews.at[idx, 'sentiment'] = 'Neutral'
                new_reviews.at[idx, 'sentiment_score'] = 0.0
        logging.info("Sentiment analysis complete.")

        # Auto-tagging
        logging.info("Auto-tagging reviews...")
        for idx, row in new_reviews.iterrows():
            try:
                if row['review_text']:
                    doc = nlp(row['review_text'].lower())
                    review_text_lower = row['review_text'].lower()
                    tags = set()
                    for tag, keywords in TAG_RULES.items():
                        if any(keyword in review_text_lower for keyword in keywords):
                            tags.add(tag)
                    new_reviews.at[idx, 'tags'] = ','.join(tags) if tags else None
                else:
                    new_reviews.at[idx, 'tags'] = None
            except Exception as e:
                logging.error(f"Error tagging review {idx}: {e}")
                new_reviews.at[idx, 'tags'] = None
        logging.info("Auto-tagging complete.")

        # Log sample DataFrame row with sentiment and tags
        logging.info(f"Sample DataFrame row with sentiment and tags: {new_reviews.iloc[0].to_dict()}")

        # Update database
        logging.info("Updating database...")
        init_db()  # Ensure table exists
        conn = sqlite3.connect('reviews.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reviews WHERE app_id = ?", (app_id,))
        new_reviews.to_sql('reviews', conn, if_exists='append', index=False)
        conn.commit()
        conn.close()
        logging.info("Database update complete.")

        # Clear the cache after refreshing reviews
        clear_reviews_cache()

        return new_reviews, f"Successfully fetched and saved {len(new_reviews)} reviews with sentiment and tags for app {app_id}!"
    except Exception as e:
        logging.error(f"Error refreshing reviews: {e}")
        return None, f"Error refreshing reviews: {e}"
