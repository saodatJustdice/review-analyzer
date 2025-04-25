import streamlit as st
import plotly.express as px
from utils import get_reviews, refresh_reviews

# Configure the app to collapse the default sidebar and use a custom navigation
st.set_page_config(
    page_title="Play Store Review Analyzer",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("Play Store Review Analyzer")

def show_home():
    st.header("Summary Statistics")
    st.markdown("Overview of review sentiment, tags, and ratings for Cash Giraffe app.")

    # Refresh button
    if st.button("Refresh Reviews", help="Fetch new reviews, analyze sentiment, and auto-tag"):
        with st.spinner("Refreshing reviews... This may take a few minutes."):
            _, message = refresh_reviews()
            st.success(message) if "Successfully" in message else st.error(message)
            st.cache_data.clear()

    df = get_reviews()
    if df.empty:
        st.warning("No reviews available. Please refresh reviews.")
        return

    # Sentiment distribution
    sentiment_counts = df['sentiment'].value_counts().reset_index()
    sentiment_counts.columns = ['Sentiment', 'Count']
    st.subheader("Sentiment Distribution")
    fig = px.bar(sentiment_counts, x='Sentiment', y='Count',
                 color='Sentiment',
                 color_discrete_map={'Positive': '#00CC96', 'Negative': '#EF553B', 'Neutral': '#AB63FA'},
                 text='Count')
    fig.update_traces(textposition='outside')
    fig.update_layout(
        height=400,
        xaxis_title="Sentiment",
        yaxis_title="Number of Reviews",
        font=dict(size=14),
        margin=dict(t=50, b=50)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Tag frequency
    tags = df['tags'].str.split(',', expand=True).stack().str.strip()
    tag_counts = tags.value_counts().head(10).reset_index()
    tag_counts.columns = ['Tag', 'Count']
    st.subheader("Top 10 Tags")
    fig = px.bar(tag_counts, x='Count', y='Tag',
                 orientation='h',
                 color='Tag',
                 color_discrete_sequence=px.colors.qualitative.Pastel,
                 text='Count')
    fig.update_traces(textposition='outside')
    fig.update_layout(
        height=400,
        xaxis_title="Number of Reviews",
        yaxis_title="Tag",
        font=dict(size=14),
        margin=dict(t=50, b=50),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

    # Rating distribution
    rating_counts = df['rating'].value_counts().sort_index().reset_index()
    rating_counts.columns = ['Rating', 'Count']
    st.subheader("Rating Distribution")
    fig = px.bar(rating_counts, x='Rating', y='Count',
                 color='Rating',
                 color_continuous_scale='Blues',
                 text='Count')
    fig.update_traces(textposition='outside')
    fig.update_layout(
        height=400,
        xaxis_title="Rating (Stars)",
        yaxis_title="Number of Reviews",
        font=dict(size=14),
        margin=dict(t=50, b=50),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

show_home()
