import streamlit as st
import pandas as pd
from db import get_reviews

def show_reviews(app_id='cashgiraffe.app'):
    st.header("Reviews")
    st.markdown("View and analyze individual reviews for the selected app.")

    try:
        df = get_reviews(app_id)
        if df.empty:
            st.warning("No reviews available. Please fetch reviews from the Home page.")
            return
    except Exception as e:
        st.error(f"Error loading reviews: {e}")
        return

    # Filters
    st.subheader("Filters")
    sentiment_filter = st.multiselect("Sentiment", options=['Positive', 'Negative', 'Neutral'], default=['Positive', 'Negative', 'Neutral'])
    rating_filter = st.slider("Rating", min_value=1, max_value=5, value=(1, 5))
    tags_filter = st.multiselect("Tags", options=sorted(set(tag for tags in df['tags'].dropna() for tag in tags.split(','))))

    # Apply filters
    filtered_df = df[
        (df['sentiment'].isin(sentiment_filter)) &
        (df['rating'].between(rating_filter[0], rating_filter[1]))
        ]
    if tags_filter:
        filtered_df = filtered_df[filtered_df['tags'].notnull()]
        filtered_df = filtered_df[filtered_df['tags'].apply(lambda x: any(tag in x.split(',') for tag in tags_filter))]

    # Display reviews
    st.subheader(f"Reviews ({len(filtered_df)})")
    for idx, row in filtered_df.iterrows():
        with st.expander(f"{row['display_username']} - {row['rating']} ★ - {row['sentiment']}"):
            st.write(f"**Date:** {row['date']}")
            st.write(f"**Review:** {row['review_text']}")
            st.write(f"**Tags:** {row['tags'] if row['tags'] else 'None'}")
