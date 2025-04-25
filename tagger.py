import logging
from config import DB_PATH
from db import load_tag_rules, add_extracted_tag
from analyzer import extract_tags_from_review
import sqlite3

# Auto-tag reviews based on current tag rules
def auto_tag_reviews(app_id):
    try:
        tag_rules = load_tag_rules(app_id)
        if not tag_rules:
            logging.info("No tag rules found.")
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT review_id, review_text FROM reviews WHERE app_id = ?", (app_id,))
        reviews = cursor.fetchall()

        for review_id, review_text in reviews:
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
                cursor.execute("UPDATE reviews SET tags = ? WHERE review_id = ?",
                               (new_tags, review_id))

        conn.commit()
        conn.close()
        logging.info("Auto-tagging completed.")
    except Exception as e:
        logging.error(f"Error auto-tagging reviews: {e}")
        raise
