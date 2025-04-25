import streamlit as st
from db import get_reviews
from utils import refresh_reviews

def show_home(app_id='cashgiraffe.app'):
    st.header("Home")
    st.markdown("Welcome to the Play Store Review Analyzer! Fetch and analyze reviews for your app.")

    if st.button("Refresh Reviews"):
        progress_placeholder = st.empty()

        def update_progress(message):
            progress_placeholder.info(message)

        with st.spinner("Fetching reviews..."):
            df, message = refresh_reviews(app_id, update_ui=update_progress)

        progress_placeholder.empty()
        if df is not None:
            st.success(message)
        else:
            st.error(message)

    try:
        df = get_reviews(app_id)
        if df.empty:
            st.warning("No reviews available. Please click 'Refresh Reviews' to fetch reviews.")
            return
    except Exception as e:
        st.error(f"Error loading reviews: {e}")
        return

    st.subheader("Summary Statistics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Reviews", len(df))
    col2.metric("Average Rating", round(df['rating'].mean(), 2))
    col3.metric("Positive Reviews", len(df[df['sentiment'] == 'Positive']))

    st.subheader("Sentiment Distribution")
    sentiment_counts = df['sentiment'].value_counts()
    st.bar_chart(sentiment_counts)

    st.subheader("Top Tags")
    if df['tags'].notnull().any():
        tags = df['tags'].str.split(',', expand=True).stack().str.strip()
        tag_counts = tags.value_counts().head(5)
        st.bar_chart(tag_counts)
    else:
        st.write("No tags available.")
