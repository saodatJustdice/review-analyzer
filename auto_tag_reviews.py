import spacy
import sqlite3
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Updated tagging rules
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

def auto_tag_reviews():
    nlp = spacy.load('en_core_web_sm')
    try:
        conn = sqlite3.connect('reviews.db')
        cursor = conn.cursor()

        # Fetch reviews without tags
        cursor.execute("SELECT review_id, review_text, sentiment FROM reviews WHERE tags IS NULL")
        reviews = cursor.fetchall()

        for review_id, review_text, sentiment in reviews:
            if review_text:
                # Extract keywords
                doc = nlp(review_text.lower())
                keywords = [token.text for token in doc if token.pos_ in ['NOUN', 'VERB', 'ADJ']]

                # Apply tagging rules
                tags = set()
                for tag, triggers in TAG_RULES.items():
                    if any(trigger in keywords for trigger in triggers):
                        tags.add(f"#{tag}")

                # Add sentiment-based tag
                if sentiment == 'Positive':
                    tags.add('#positive')
                elif sentiment == 'Negative':
                    tags.add('#negative')

                # Update database
                tags_str = ','.join(tags) if tags else ''
                cursor.execute('''
                               UPDATE reviews
                               SET tags = ?
                               WHERE review_id = ?
                               ''', (tags_str, review_id))

        conn.commit()
        logging.info(f"Auto-tagged {len(reviews)} reviews.")
        print(f"Auto-tagged {len(reviews)} reviews.")

    except sqlite3.Error as e:
        logging.error(f"Error auto-tagging: {e}")
        print(f"Error auto-tagging: {e}")

    finally:
        conn.close()

if __name__ == "__main__":
    auto_tag_reviews()
