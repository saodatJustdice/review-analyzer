import sqlite3
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_statistics():
    try:
        conn = sqlite3.connect('reviews.db')
        # Load reviews into Pandas DataFrame
        df = pd.read_sql_query("SELECT * FROM reviews", conn)
        conn.close()

        # Sentiment distribution
        sentiment_counts = df['sentiment'].value_counts()
        logging.info("Sentiment Distribution:")
        print("Sentiment Distribution:")
        print(sentiment_counts)

        # Tag frequency
        tags = df['tags'].str.split(',', expand=True).stack().str.strip()
        tag_counts = tags.value_counts()
        logging.info("\nTag Frequency:")
        print("\nTag Frequency:")
        print(tag_counts.head(10))

        # Rating distribution
        rating_counts = df['rating'].value_counts().sort_index()
        logging.info("\nRating Distribution:")
        print("\nRating Distribution:")
        print(rating_counts)

        # Average sentiment score and rating by tag
        tag_stats = df.explode('tags').groupby('tags').agg({
            'sentiment_score': 'mean',
            'rating': 'mean',
            'review_id': 'count'
        }).rename(columns={'review_id': 'count'})
        logging.info("\nTag Statistics:")
        print("\nTag Statistics:")
        print(tag_stats.head(10))

        # Export to CSV
        sentiment_counts.to_csv('sentiment_distribution.csv')
        tag_counts.to_csv('tag_frequency.csv')
        rating_counts.to_csv('rating_distribution.csv')
        tag_stats.to_csv('tag_statistics.csv')
        logging.info("Statistics exported to CSV files.")
        print("Statistics exported to CSV files.")

    except Exception as e:
        logging.error(f"Error generating statistics: {e}")
        print(f"Error generating statistics: {e}")

if __name__ == "__main__":
    generate_statistics()
