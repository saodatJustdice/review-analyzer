import streamlit as st
from pages.home import show_home
from pages.reviews import show_reviews
from pages.trends import show_trends
from pages.tags import show_tags
from db import get_app_ids, add_app_id, clear_reviews_cache
# Configure the app to collapse the default sidebar and use a custom navigation
st.set_page_config(
    page_title="Play Store Review Analyzer",
    layout="wide",
    initial_sidebar_state="collapsed"
)

with open('./style.css') as f:
    css = f.read()

st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

# Clear cache on app start to ensure fresh data
clear_reviews_cache()

st.title("Play Store Review Analyzer")

# Fetch app IDs from the database
app_ids = get_app_ids()

# App selection
st.sidebar.header("App Selection")
app_id = st.sidebar.selectbox("Choose an app", app_ids)

# Form to add a new app ID
with st.sidebar.expander("Add New App", expanded=False):
    new_app_id = st.text_input("Enter new app ID (e.g., com.example.app)", "")
    if st.button("Add App"):
        try:
            add_app_id(new_app_id)
            st.success(f"Added app ID: {new_app_id}")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Error adding app ID: {e}")

# Custom navigation in the sidebar
st.sidebar.header("Navigation")
page = st.sidebar.selectbox("Choose a page", ["Home", "Reviews", "Trends", "Tags"])

# Render the selected page
if page == "Home":
    show_home(app_id)
elif page == "Reviews":
    show_reviews(app_id)
elif page == "Trends":
    show_trends(app_id)
elif page == "Tags":
    show_tags(app_id)
