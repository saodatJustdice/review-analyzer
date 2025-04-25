import sqlite3
import pandas as pd
import psycopg2
from psycopg2 import sql
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# SQLite connection
def get_sqlite_data():
    try:
        conn = sqlite3.connect('reviews.db')
        df = pd.read_sql_query("SELECT * FROM reviews", conn)
        conn.close()
        logging.info(f"Fetched {len(df)} reviews from SQLite.")
        return df
    except Exception as e:
        logging.error(f"Error reading from SQLite: {e}")
        return None

# PostgreSQL connection
def init_postgres():
    try:
        conn = psycopg2.connect(
            dbname="reviews",
            user="saodatJustdice",
            password="",  # Replace with your PostgreSQL password
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        # Create reviews table
        cursor.execute("""
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
            );
        """)
        conn.commit()
        logging.info("PostgreSQL table initialized successfully.")
        return conn
    except Exception as e:
        logging.error(f"Error initializing PostgreSQL: {e}")
        return None

# Migrate data
def migrate_data():
    # Fetch data from SQLite
    df = get_sqlite_data()
    if df is None or df.empty:
        logging.error("No data to migrate.")
        return

    # Connect to PostgreSQL
    conn = init_postgres()
    if conn is None:
        return

    cursor = conn.cursor()
    try:
        # Clear existing data (optional, remove if you want to append)
        cursor.execute("DELETE FROM reviews;")

        # Insert data into PostgreSQL
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO reviews (app_id, review_id, username, date, rating, review_text, sentiment, sentiment_score, tags)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (review_id) DO NOTHING;
            """, (
                row['app_id'],
                row['review_id'],
                row['username'],
                str(row['date']),  # Convert Timestamp to string
                row['rating'],
                row['review_text'],
                row['sentiment'],
                row['sentiment_score'],
                row['tags']
            ))
        conn.commit()
        logging.info(f"Migrated {len(df)} reviews to PostgreSQL.")
    except Exception as e:
        logging.error(f"Error migrating data to PostgreSQL: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    migrate_data()
