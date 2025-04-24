from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import sqlite3
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def analyze_sentiment():
    analyzer = SentimentIntensityAnalyzer()
    try:
        conn = sqlite3.connect('reviews.db')
        cursor = conn.cursor()

        # Fetch reviews without sentiment
        cursor.execute("SELECT review_id, review_text FROM reviews WHERE sentiment IS NULL")
        reviews = cursor.fetchall()

        for review_id, review_text in reviews:
            if review_text:
                # Analyze sentiment
                scores = analyzer.polarity_scores(review_text)
                compound = scores['compound']
                sentiment = (
                    'Positive' if compound > 0.05 else
                    'Negative' if compound < -0.05 else
                    'Neutral'
                )
                # Update database
                cursor.execute('''
                               UPDATE reviews
                               SET sentiment = ?, sentiment_score = ?
                               WHERE review_id = ?
                               ''', (sentiment, compound, review_id))

        conn.commit()
        logging.info(f"Analyzed sentiment for {len(reviews)} reviews.")
        print(f"Analyzed sentiment for {len(reviews)} reviews.")

    except sqlite3.Error as e:
        logging.error(f"Error analyzing sentiment: {e}")
        print(f"Error analyzing sentiment: {e}")

    finally:
        conn.close()

if __name__ == "__main__":
    analyze_sentiment()
