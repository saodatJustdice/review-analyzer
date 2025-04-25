import streamlit as st
import pandas as pd
from db import get_reviews, clear_reviews_cache
from datetime import datetime, timedelta

def show_reviews(app_id='cashgiraffe.app'):
    st.header("Reviews")
    st.markdown("View and analyze individual reviews for the selected app.")

    try:
        #Fetch all reviews to initialize the date filter
        clear_reviews_cache()
        df = get_reviews(app_id)
        if df.empty:
            st.warning("No reviews available. Please fetch reviews from the Home page.")
            return
    except Exception as e:
        st.error(f"Error loading reviews: {e}")
        return

    if 'reviews_page' not in st.session_state:
        st.session_state['reviews_page'] = 0

    with st.sidebar:
        st.subheader("Date Filter")
        min_date = df['date'].min()
        max_date = df['date'].max()
        date_range = st.date_input("Date Range", [min_date, max_date], key="date_range")





        if len(date_range) == 2:
            start_date = date_range[0]
            end_date = date_range[1]

            if start_date > end_date:
                st.warning("Start date must be before end date.")
                return
                # Fetch reviews based on the date_range
            df = get_reviews(app_id, start_date, end_date)



        st.subheader("Filters")
        sentiment_filter = st.multiselect("Sentiment", options=['Positive', 'Negative', 'Neutral'],
                                          default=['Positive', 'Negative', 'Neutral'], on_change=clear_reviews_cache)
        rating_filter = st.slider("Rating", min_value=1, max_value=5, value=(1, 5), on_change=clear_reviews_cache)
        tags_filter = st.multiselect("Tags",
                                     options=sorted(
                                         set(tag for tags in df['tags'].dropna() for tag in tags.split(','))), on_change=clear_reviews_cache)




    filtered_df = df


    # Apply other filters
    filtered_df = filtered_df[
        (filtered_df['sentiment'].isin(sentiment_filter)) &
        (filtered_df['rating'].between(rating_filter[0], rating_filter[1]))
        ]
    if tags_filter:
        filtered_df = filtered_df[filtered_df['tags'].notnull()]
        filtered_df = filtered_df[filtered_df['tags'].apply(lambda x: any(tag in x.split(',') for tag in tags_filter))]

    total_reviews = len(filtered_df)

    # Pagination
    st.sidebar.subheader("Pagination")
    items_per_page = st.sidebar.selectbox("Items per page", [10, 20, 50, 100], index=1)
    total_pages = (total_reviews + items_per_page - 1) // items_per_page

    if total_pages > 1:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Previous", key="previous_button", disabled=(st.session_state['reviews_page'] == 0)):
                st.session_state['reviews_page'] -= 1
                clear_reviews_cache()
        with col2:
            if st.button("Next", key="next_button", disabled=(st.session_state['reviews_page'] == total_pages -1)):
                st.session_state['reviews_page'] += 1
                clear_reviews_cache()

    start_index = st.session_state['reviews_page'] * items_per_page
    end_index = start_index + items_per_page
    paginated_df = filtered_df[start_index:end_index]

    # Apply deferred operations
    paginated_df['date'] = pd.to_datetime(paginated_df['date'])
    has_duplicates = paginated_df['username'].duplicated().any()
    if has_duplicates:
        paginated_df['display_username'] = paginated_df.apply(lambda x: f"{x['username']} (ID: {x['review_id'][-4:]})", axis=1)
    else:
        paginated_df['display_username'] = paginated_df['username']

    st.subheader(f"Reviews ({total_reviews})")
    if total_reviews > 0:
        for idx, row in paginated_df.iterrows():
            with st.expander(f"{row['display_username']} - {row['rating']} ★ - {row['sentiment']}", expanded=1):
                st.write(f"**Date:** {row['date']}")
                st.write(f"**Review:** {row['review_text']}")
                st.write(f"**Tags:** {row['tags'] if row['tags'] else 'None'}")
    else:
        st.write("No results found")

