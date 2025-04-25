import pandas as pd
import logging
from fetcher import fetch_all_reviews
from analyzer import analyze_sentiment, extract_tags_from_review
from tagger import auto_tag_reviews
from db import init_db, get_reviews, clear_reviews_cache, get_app_ids, add_app_id, load_tag_rules, add_extracted_tag
from config import DB_PATH
import sqlite3

# Fetch reviews, analyze sentiment, and auto-tag, with UI updates
def refresh_reviews(app_id='cashgiraffe.app', update_ui=None):
    try:
        all_reviews = fetch_all_reviews(app_id, batch_size=100, delay=10, update_ui=update_ui)

        message = "Finished fetching reviews."
        logging.info(message)
        if update_ui:
            update_ui(message)

        if not all_reviews:
            message = "No new reviews fetched."
            if update_ui:
                update_ui(message)
            return None, message

        message = f"Total reviews fetched: {len(all_reviews)}"
        logging.info(message)
        if update_ui:
            update_ui(message)

        message = f"Sample review data (raw): {all_reviews[0] if all_reviews else 'No data'}"
        logging.info(message)
        if update_ui:
            update_ui(message)

        cleaned_reviews = []
        for review in all_reviews:
            try:
                def extract_value(field, default=''):
                    if isinstance(field, dict) and 'value' in field:
                        return str(field['value'])
                    return str(field) if field is not None else default

                cleaned_review = {
                    'app_id': app_id,
                    'reviewId': extract_value(review.get('reviewId', '')),
                    'userName': extract_value(review.get('userName', '')),
                    'at': review.get('at'),
                    'score': int(extract_value(review.get('score', 0), 0)) if review.get('score') is not None else 0,
                    'content': extract_value(review.get('content', ''))
                }
                for key in ['reviewId', 'userName', 'score', 'content']:
                    field = review.get(key)
                    if isinstance(field, dict):
                        message = f"Nested field found for {key}: {field}"
                        logging.warning(message)
                        if update_ui:
                            update_ui(message)
                    elif not isinstance(field, (str, int, type(None))):
                        message = f"Unexpected type for {key}: {field} (type: {type(field)})"
                        logging.warning(message)
                        if update_ui:
                            update_ui(message)
                cleaned_reviews.append(cleaned_review)
            except Exception as e:
                message = f"Error processing review: {review}, Error: {e}"
                logging.error(message)
                if update_ui:
                    update_ui(message)
                continue

        if not cleaned_reviews:
            message = "No reviews after cleaning."
            if update_ui:
                update_ui(message)
            return None, message

        message = f"Sample review data (cleaned): {cleaned_reviews[0]}"
        logging.info(message)
        if update_ui:
            update_ui(message)

        message = "Converting to DataFrame..."
        logging.info(message)
        if update_ui:
            update_ui(message)
        new_reviews = pd.DataFrame(cleaned_reviews)
        message = "DataFrame conversion complete."
        logging.info(message)
        if update_ui:
            update_ui(message)

        new_reviews = new_reviews.rename(columns={
            'reviewId': 'review_id',
            'userName': 'username',
            'at': 'date',
            'score': 'rating',
            'content': 'review_text'
        })
        required_columns = ['app_id', 'review_id', 'username', 'date', 'rating', 'review_text']
        new_reviews = new_reviews[required_columns]

        new_reviews['sentiment'] = None
        new_reviews['sentiment_score'] = None
        new_reviews['tags'] = None

        message = "Analyzing sentiment..."
        logging.info(message)
        if update_ui:
            update_ui(message)
        for idx, row in new_reviews.iterrows():
            try:
                sentiment, score = analyze_sentiment(row['review_text'])
                new_reviews.at[idx, 'sentiment'] = sentiment
                new_reviews.at[idx, 'sentiment_score'] = score
            except Exception as e:
                message = f"Error analyzing sentiment for review {idx}: {e}"
                logging.error(message)
                if update_ui:
                    update_ui(message)
                new_reviews.at[idx, 'sentiment'] = 'Neutral'
                new_reviews.at[idx, 'sentiment_score'] = 0.0
        message = "Sentiment analysis complete."
        logging.info(message)
        if update_ui:
            update_ui(message)

        message = "Auto-tagging and extracting tags from reviews..."
        logging.info(message)
        if update_ui:
            update_ui(message)
        tag_rules = load_tag_rules(app_id)
        for idx, row in new_reviews.iterrows():
            try:
                if row['review_text']:
                    review_text_lower = row['review_text'].lower()
                    tags = set()
                    for tag, keywords in tag_rules.items():
                        if any(keyword in review_text_lower for keyword in keywords):
                            tags.add(tag)
                    extracted_tags = extract_tags_from_review(row['review_text'])
                    for tag in extracted_tags:
                        tags.add(tag)
                        add_extracted_tag(app_id, tag)
                    new_reviews.at[idx, 'tags'] = ','.join(tags) if tags else None
                else:
                    new_reviews.at[idx, 'tags'] = None
            except Exception as e:
                message = f"Error tagging review {idx}: {e}"
                logging.error(message)
                if update_ui:
                    update_ui(message)
                new_reviews.at[idx, 'tags'] = None
        message = "Auto-tagging and extraction complete."
        logging.info(message)
        if update_ui:
            update_ui(message)

        message = f"Sample DataFrame row with sentiment and tags: {new_reviews.iloc[0].to_dict()}"
        logging.info(message)
        if update_ui:
            update_ui(message)

        message = "Updating database..."
        logging.info(message)
        if update_ui:
            update_ui(message)
        init_db()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reviews WHERE app_id = ?", (app_id,))
        new_reviews.to_sql('reviews', conn, if_exists='append', index=False)
        conn.commit()
        conn.close()
        message = "Database update complete."
        logging.info(message)
        if update_ui:
            update_ui(message)

        clear_reviews_cache()

        message = f"Successfully fetched and saved {len(new_reviews)} reviews with sentiment and tags for app {app_id}!"
        return new_reviews, message
    except Exception as e:
        message = f"Error refreshing reviews: {e}"
        logging.error(message)
        if update_ui:
            update_ui(message)
        return None, message
