import streamlit as st
import pandas as pd
import altair as alt
from db import get_reviews

def show_trends(app_id='cashgiraffe.app'):
    st.header("Trends")
    st.markdown("Analyze trends in reviews over time for the selected app.")

    try:
        df = get_reviews(app_id)
        if df.empty:
            st.warning("No reviews available. Please fetch reviews from the Home page.")
            return
    except Exception as e:
        st.error(f"Error loading reviews: {e}")
        return

    # Date range filter
    st.subheader("Date Range")
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()
    date_range = st.date_input("Select date range", [min_date, max_date], min_value=min_date, max_value=max_date)

    if len(date_range) != 2:
        st.error("Please select a valid date range.")
        return

    start_date, end_date = date_range
    filtered_df = df[(df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)]

    if filtered_df.empty:
        st.warning("No reviews in the selected date range.")
        return

    # Rating trend
    st.subheader("Average Rating Over Time")
    rating_trend = filtered_df.groupby(filtered_df['date'].dt.date)['rating'].mean().reset_index()
    rating_chart = alt.Chart(rating_trend).mark_line().encode(
        x='date:T',
        y='rating:Q',
        tooltip=['date', 'rating']
    ).properties(width=700, height=300)
    st.altair_chart(rating_chart)

    # Sentiment trend
    st.subheader("Sentiment Distribution Over Time")
    sentiment_trend = filtered_df.groupby([filtered_df['date'].dt.date, 'sentiment']).size().unstack().fillna(0).reset_index()
    sentiment_melted = sentiment_trend.melt('date', var_name='sentiment', value_name='count')
    sentiment_chart = alt.Chart(sentiment_melted).mark_area().encode(
        x='date:T',
        y=alt.Y('count:Q', stack=True),
        color='sentiment:N',
        tooltip=['date', 'sentiment', 'count']
    ).properties(width=700, height=300)
    st.altair_chart(sentiment_chart)

    # Tag trend
    st.subheader("Tag Trends Over Time")
    if filtered_df['tags'].notnull().any():
        tags_df = filtered_df[['date', 'tags']].copy()
        tags_df = tags_df[tags_df['tags'].notnull()]
        tags_df['tags'] = tags_df['tags'].str.split(',')
        tags_exploded = tags_df.explode('tags')
        tags_exploded['tags'] = tags_exploded['tags'].str.strip()
        tag_trend = tags_exploded.groupby([tags_exploded['date'].dt.date, 'tags']).size().unstack().fillna(0).reset_index()
        top_tags = tags_exploded['tags'].value_counts().head(5).index
        tag_trend = tag_trend[['date'] + list(top_tags)]
        tag_melted = tag_trend.melt('date', var_name='tags', value_name='count')
        tag_chart = alt.Chart(tag_melted).mark_line().encode(
            x='date:T',
            y='count:Q',
            color='tags:N',
            tooltip=['date', 'tags', 'count']
        ).properties(width=700, height=300)
        st.altair_chart(tag_chart)
    else:
        st.write("No tags available.")
