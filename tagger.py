import logging
import sqlite3
from config import DB_PATH
from db import load_tag_rules, add_extracted_tag
from analyzer import extract_tags_from_review


# Auto-tag reviews based on current tag rules
def auto_tag_reviews(app_id):
    try:
        tag_rules = load_tag_rules(app_id)
        if not tag_rules:
            logging.info("No tag rules found for app_id: %s", app_id)
            return

        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT review_id, review_text FROM reviews WHERE app_id = ?", (app_id,))
            reviews = cursor.fetchall()
        except sqlite3.Error as e:
            logging.error("Error connecting to the database: %s", e)
            raise
        finally:
            if conn:
                conn.close()

        for review_id, review_text in reviews:
            try:
                if review_text:
                    review_text_lower = review_text.lower()
                    tags = set()
                    for tag, keywords in tag_rules.items():
                        if any(keyword in review_text_lower for keyword in keywords):
                            tags.add(tag)
                    extracted = extract_tags_from_review(review_text)
                    for tag in extracted:
                        tags.add(tag)
                        add_extracted_tag(app_id, tag)
                    new_tags = ','.join(tags) if tags else None
                    conn = sqlite3.connect(DB_PATH)
                    cursor = conn.cursor()
                    cursor.execute("UPDATE reviews SET tags = ? WHERE review_id = ?", (new_tags, review_id))
                    conn.commit()
            except sqlite3.Error as e:
                logging.error(f"Error auto-tagging review {review_id}: {e}")
            finally:
                if conn:
                    conn.close()
        logging.info("Auto-tagging completed for app_id: %s", app_id)
    except Exception as e:
        logging.error(f"Error auto-tagging reviews: {e}")
        raise
