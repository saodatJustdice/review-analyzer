import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def analyze_trends():
    try:
        conn = sqlite3.connect('reviews.db')
        df = pd.read_sql_query("SELECT * FROM reviews", conn)
        conn.close()

        # Convert date to datetime
        df['date'] = pd.to_datetime(df['date'])
        df['date_only'] = df['date'].dt.date

        # Daily sentiment distribution
        daily_sentiment = df.groupby(['date_only', 'sentiment']).size().unstack(fill_value=0)
        daily_sentiment_pct = daily_sentiment.div(daily_sentiment.sum(axis=1), axis=0) * 100

        # Plot sentiment trends
        plt.figure(figsize=(12, 6))
        daily_sentiment_pct.plot()
        plt.title('Daily Sentiment Distribution (%)')
        plt.xlabel('Date')
        plt.ylabel('Percentage')
        plt.legend(title='Sentiment')
        plt.savefig('sentiment_trends.png')
        plt.close()

        # Tag trends (top 5 tags)
        top_tags = df['tags'].str.split(',', expand=True).stack().value_counts().head(5).index
        df_tags = df.explode('tags')
        tag_trends = df_tags[df_tags['tags'].isin(top_tags)].groupby(['date_only', 'tags']).size().unstack(fill_value=0)

        # Plot tag trends
        plt.figure(figsize=(12, 6))
        tag_trends.plot()
        plt.title('Top 5 Tag Trends')
        plt.xlabel('Date')
        plt.ylabel('Count')
        plt.legend(title='Tags')
        plt.savefig('tag_trends.png')
        plt.close()

        # Rating trends (weekly)
        df['week'] = df['date'].dt.to_period('W').apply(lambda r: r.start_time)
        weekly_rating = df.groupby('week')['rating'].mean()

        # Plot rating trends
        plt.figure(figsize=(12, 6))
        weekly_rating.plot()
        plt.title('Weekly Average Rating')
        plt.xlabel('Week')
        plt.ylabel('Average Rating')
        plt.savefig('rating_trends.png')
        plt.close()

        # Sentiment vs. rating correlation
        correlation = df[['sentiment_score', 'rating']].corr().iloc[0, 1]
        logging.info(f"Sentiment Score vs. Rating Correlation: {correlation:.3f}")
        print(f"Sentiment Score vs. Rating Correlation: {correlation:.3f}")

        # Export trends to CSV
        daily_sentiment_pct.to_csv('daily_sentiment_trends.csv')
        tag_trends.to_csv('tag_trends.csv')
        weekly_rating.to_csv('weekly_rating_trends.csv')
        logging.info("Trends exported to CSV files.")
        print("Trends exported to CSV files.")

    except Exception as e:
        logging.error(f"Error analyzing trends: {e}")
        print(f"Error analyzing trends: {e}")

if __name__ == "__main__":
    analyze_trends()
