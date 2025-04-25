import streamlit as st
import plotly.express as px
from utils import get_reviews
from datetime import datetime, timedelta

def show_trends():
    st.header("Trend Analysis")
    st.markdown("Interactive charts showing sentiment and tag trends over time.")
    df = get_reviews()
    if df.empty:
        st.warning("No reviews available. Please refresh reviews on the Home page.")
        return

    # Calculate default date range (last 30 days)
    end_date = datetime(2025, 4, 24)  # Current date
    start_date = end_date - timedelta(days=30)  # 30 days ago

    # Date range filter with default to last 30 days
    st.subheader("Filter by Date Range")
    date_range = st.date_input(
        "Select Date Range",
        value=[start_date.date(), end_date.date()],
        min_value=df['date'].min().date(),
        max_value=df['date'].max().date()
    )

    # Handle date range input (it returns a tuple or single date)
    if len(date_range) == 2:
        filter_start_date, filter_end_date = date_range
    else:
        filter_start_date, filter_end_date = start_date.date(), end_date.date()

    # Filter reviews based on the selected date range
    filtered_df = df[
        (df['date'].dt.date >= filter_start_date) &
        (df['date'].dt.date <= filter_end_date)
        ]

    if filtered_df.empty:
        st.warning("No reviews available for the selected date range.")
        return

    # Daily sentiment trends
    filtered_df['date_only'] = filtered_df['date'].dt.date
    daily_sentiment = filtered_df.groupby(['date_only', 'sentiment']).size().unstack(fill_value=0)
    daily_sentiment_pct = daily_sentiment.div(daily_sentiment.sum(axis=1), axis=0) * 100
    daily_sentiment_pct = daily_sentiment_pct.reset_index()

    st.subheader("Daily Sentiment Trends (%)")
    fig = px.line(daily_sentiment_pct, x='date_only', y=daily_sentiment_pct.columns[1:],
                  title='Daily Sentiment Distribution (%)',
                  labels={'value': 'Percentage', 'date_only': 'Date', 'variable': 'Sentiment'})
    fig.update_layout(hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)

    # Tag trends (top 5 tags)
    top_tags = filtered_df['tags'].str.split(',', expand=True).stack().value_counts().head(5).index
    df_tags = filtered_df.explode('tags')
    tag_trends = df_tags[df_tags['tags'].isin(top_tags)].groupby(['date_only', 'tags']).size().unstack(fill_value=0)
    tag_trends = tag_trends.reset_index()

    st.subheader("Top 5 Tag Trends")
    fig = px.line(tag_trends, x='date_only', y=tag_trends.columns[1:],
                  title='Top 5 Tag Trends',
                  labels={'value': 'Count', 'date_only': 'Date', 'variable': 'Tag'})
    fig.update_layout(hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)

show_trends()
