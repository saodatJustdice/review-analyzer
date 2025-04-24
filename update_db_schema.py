import sqlite3
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def update_database_schema():
    try:
        conn = sqlite3.connect('reviews.db')
        cursor = conn.cursor()

        # Add sentiment, sentiment_score, and tags columns if they don't exist
        cursor.execute("ALTER TABLE reviews ADD COLUMN sentiment TEXT")
        cursor.execute("ALTER TABLE reviews ADD COLUMN sentiment_score REAL")
        cursor.execute("ALTER TABLE reviews ADD COLUMN tags TEXT")

        conn.commit()
        logging.info("Database schema updated successfully.")
        print("Database schema updated successfully.")

    except sqlite3.Error as e:
        logging.error(f"Error updating schema: {e}")
        print(f"Error updating schema: {e}")

    finally:
        conn.close()

if __name__ == "__main__":
    update_database_schema()
