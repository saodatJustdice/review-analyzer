import streamlit as st
import sqlite3
import pandas as pd
from utils import get_reviews, clear_reviews_cache

def show_reviews():
    st.header("Review Management")
    st.markdown("Filter reviews by sentiment, tags, or date, and manually add tags.")
    df = get_reviews()
    if df.empty:
        st.warning("No reviews available. Please refresh reviews on the Home page.")
        return

    # Filters
    with st.expander("Filter Reviews", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            sentiment_filter = st.multiselect(
                "Sentiment",
                options=df['sentiment'].unique(),
                default=df['sentiment'].unique(),
                help="Select one or more sentiments to filter reviews."
            )
        with col2:
            tags = df['tags'].str.split(',', expand=True).stack().str.strip().unique()
            tags = [tag for tag in tags if tag]  # Remove empty tags
            tag_filter = st.multiselect(
                "Tags",
                options=tags,
                default=[],
                help="Select tags to filter reviews (e.g., #payment)."
            )
        date_range = st.date_input(
            "Date Range",
            [df['date'].min(), df['date'].max()],
            help="Choose a date range for reviews."
        )

    # Apply filters
    filtered_df = df[df['sentiment'].isin(sentiment_filter)]
    if tag_filter:
        # Ensure tags column is treated as a string, handle None/nan
        filtered_df = filtered_df[
            filtered_df['tags'].apply(
                lambda x: any(tag in str(x).split(',') for tag in tag_filter) if pd.notna(x) and x != '' else False
            )
        ]
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (filtered_df['date'].dt.date >= start_date) &
            (filtered_df['date'].dt.date <= end_date)
            ]
    else:
        st.warning("Please select a valid date range.")
        return

    # Display filtered reviews
    st.subheader(f"Filtered Reviews ({len(filtered_df)})")
    display_df = filtered_df[['username', 'rating', 'review_text', 'sentiment', 'tags', 'date']].copy()
    display_df['review_text'] = display_df['review_text'].apply(
        lambda x: x[:100] + '...' if len(x) > 100 else x
    )
    st.dataframe(display_df, use_container_width=True)

    # Manual tagging
    with st.expander("Manual Tagging", expanded=False):
        st.markdown("Select a user to update their review tags.")
        selected_username = st.selectbox(
            "Select Username",
            options=filtered_df['display_username'],
            help="Choose a user to tag their review."
        )
        selected_review = filtered_df[filtered_df['display_username'] == selected_username]
        if not selected_review.empty:
            st.write(f"**Review Text**: {selected_review['review_text'].iloc[0]}")
            current_tags = selected_review['tags'].iloc[0]
            st.write(f"**Current Tags**: {current_tags or 'None'}")
            new_tags = st.text_input(
                "Add Tags (comma-separated, e.g., bug,new)",
                help="Enter new tags to add to the review (without #)."
            )
            if st.button("Update Tags"):
                if new_tags:
                    # Normalize new tags: remove spaces, remove #, split by comma
                    new_tags_list = [tag.strip().replace('#', '') for tag in new_tags.split(',') if tag.strip()]
                    if not new_tags_list:
                        st.error("Please enter valid tags.")
                        return
                    new_tags = ','.join(new_tags_list)

                    # Update the database
                    conn = sqlite3.connect('reviews.db')
                    cursor = conn.cursor()
                    updated_tags = ','.join(set(current_tags.split(',') + new_tags.split(',')) - {''}) if current_tags else new_tags
                    review_id = selected_review['review_id'].iloc[0]
                    cursor.execute("UPDATE reviews SET tags = ? WHERE review_id = ?", (updated_tags, review_id))
                    conn.commit()

                    # Check if the update was successful
                    if cursor.rowcount == 0:
                        conn.close()
                        st.error(f"Failed to update tags for {selected_username}. Review ID {review_id} not found in the database.")
                        return

                    conn.close()
                    st.success(f"Tags updated for {selected_username}: {updated_tags}")

                    # Clear the cache and refresh the page
                    clear_reviews_cache()
                    st.experimental_rerun()
                else:
                    st.error("Please enter at least one tag.")

    # Export filtered reviews
    with st.expander("Export Reviews", expanded=False):
        st.markdown("Download the filtered reviews as a CSV file.")
        if st.button("Download Filtered Reviews as CSV"):
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="filtered_reviews.csv",
                mime="text/csv"
            )
            st.success("Filtered reviews ready for download!")

show_reviews()
