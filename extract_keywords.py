import spacy
import sqlite3
from collections import Counter
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_keywords():
    nlp = spacy.load('en_core_web_sm')
    try:
        conn = sqlite3.connect('reviews.db')
        cursor = conn.cursor()

        # Fetch all reviews
        cursor.execute("SELECT review_text FROM reviews WHERE review_text IS NOT NULL")
        reviews = cursor.fetchall()

        # Extract keywords
        all_keywords = []
        for review_text, in reviews:
            doc = nlp(review_text.lower())
            keywords = [token.text for token in doc if token.pos_ in ['NOUN', 'VERB', 'ADJ'] and token.is_alpha]
            all_keywords.extend(keywords)

        # Count keyword frequencies
        keyword_counts = Counter(all_keywords)

        # Log top 50 keywords
        logging.info("Top 50 keywords:")
        print("Top 50 keywords:")
        for keyword, count in keyword_counts.most_common(50):
            logging.info(f"{keyword}: {count}")
            print(f"{keyword}: {count}")

        conn.close()
        return keyword_counts

    except Exception as e:
        logging.error(f"Error extracting keywords: {e}")
        print(f"Error extracting keywords: {e}")
        return None

if __name__ == "__main__":
    extract_keywords()
