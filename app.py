import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database connection
def get_reviews():
    conn = sqlite3.connect('reviews.db')
    df = pd.read_sql_query("SELECT * FROM reviews", conn)
    conn.close()
    df['date'] = pd.to_datetime(df['date'])
    return df

# Streamlit app
st.title("TheTestEmall Review Analyzer")

# Sidebar for navigation
page = st.sidebar.selectbox("Choose a page", ["Home", "Trends", "Reviews"])

# Home Page: Summary Statistics
if page == "Home":
    st.header("Summary Statistics")
    df = get_reviews()

    # Sentiment distribution
    sentiment_counts = df['sentiment'].value_counts()
    st.subheader("Sentiment Distribution")
    st.bar_chart(sentiment_counts)

    # Tag frequency
    tags = df['tags'].str.split(',', expand=True).stack().str.strip()
    tag_counts = tags.value_counts().head(10)
    st.subheader("Top 10 Tags")
    st.bar_chart(tag_counts)

    # Rating distribution
    rating_counts = df['rating'].value_counts().sort_index()
    st.subheader("Rating Distribution")
    st.bar_chart(rating_counts)

# Trends Page: Visualizations
elif page == "Trends":
    st.header("Trend Analysis")
    df = get_reviews()

    # Daily sentiment trends
    df['date_only'] = df['date'].dt.date
    daily_sentiment = df.groupby(['date_only', 'sentiment']).size().unstack(fill_value=0)
    daily_sentiment_pct = daily_sentiment.div(daily_sentiment.sum(axis=1), axis=0) * 100

    st.subheader("Daily Sentiment Trends (%)")
    fig, ax = plt.subplots(figsize=(10, 5))
    daily_sentiment_pct.plot(ax=ax)
    ax.set_title('Daily Sentiment Distribution (%)')
    ax.set_xlabel('Date')
    ax.set_ylabel('Percentage')
    st.pyplot(fig)

    # Tag trends
    top_tags = df['tags'].str.split(',', expand=True).stack().value_counts().head(5).index
    df_tags = df.explode('tags')
    tag_trends = df_tags[df_tags['tags'].isin(top_tags)].groupby(['date_only', 'tags']).size().unstack(fill_value=0)

    st.subheader("Top 5 Tag Trends")
    fig, ax = plt.subplots(figsize=(10, 5))
    tag_trends.plot(ax=ax)
    ax.set_title('Top 5 Tag Trends')
    ax.set_xlabel('Date')
    ax.set_ylabel('Count')
    st.pyplot(fig)

# Reviews Page: Filter and Tag
elif page == "Reviews":
    st.header("Review Management")
    df = get_reviews()

    # Filters
    st.subheader("Filter Reviews")
    sentiment_filter = st.multiselect("Sentiment", options=df['sentiment'].unique(), default=df['sentiment'].unique())
    tags = df['tags'].str.split(',', expand=True).stack().str.strip().unique()
    tag_filter = st.multiselect("Tags", options=tags, default=[])
    date_range = st.date_input("Date Range", [df['date'].min(), df['date'].max()])

    # Apply filters
    filtered_df = df[df['sentiment'].isin(sentiment_filter)]
    if tag_filter:
        filtered_df = filtered_df[filtered_df['tags'].apply(lambda x: any(tag in x for tag in tag_filter) if pd.notnull(x) else False)]
    filtered_df = filtered_df[(filtered_df['date'].dt.date >= date_range[0]) & (filtered_df['date'].dt.date <= date_range[1])]

    st.subheader(f"Filtered Reviews ({len(filtered_df)})")
    st.dataframe(filtered_df[['review_id', 'username', 'rating', 'review_text', 'sentiment', 'tags', 'date']])

    # Manual tagging
    st.subheader("Manual Tagging")
    review_id = st.selectbox("Select Review ID", filtered_df['review_id'])
    selected_review = filtered_df[filtered_df['review_id'] == review_id]
    if not selected_review.empty:
        st.write(f"Review Text: {selected_review['review_text'].iloc[0]}")
        current_tags = selected_review['tags'].iloc[0]
        st.write(f"Current Tags: {current_tags or 'None'}")
        new_tags = st.text_input("Add Tags (comma-separated, e.g., #bug,#new)")
        if st.button("Update Tags"):
            conn = sqlite3.connect('reviews.db')
            cursor = conn.cursor()
            updated_tags = ','.join(set(current_tags.split(',') + new_tags.split(',')) - {''}) if current_tags else new_tags
            cursor.execute("UPDATE reviews SET tags = ? WHERE review_id = ?", (updated_tags, review_id))
            conn.commit()
            conn.close()
            st.success(f"Tags updated: {updated_tags}")

    # Export filtered reviews
    st.subheader("Export Reviews")
    if st.button("Download Filtered Reviews as CSV"):
        filtered_df.to_csv('filtered_reviews.csv', index=False)
        st.success("Filtered reviews exported to filtered_reviews.csv")

logging.info(f"Streamlit app running on page: {page}")
