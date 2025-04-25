import spacy
import logging
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Load spaCy model
try:
    nlp = spacy.load('en_core_web_sm')
except Exception as e:
    logging.error(f"Error loading spaCy model: {e}")
    raise

# Extract tags from review text using spaCy
def extract_tags_from_review(review_text):
    try:
        if not review_text:
            return []
        doc = nlp(review_text.lower())
        tags = set()
        for chunk in doc.noun_chunks:
            tag = chunk.text.replace(' ', '-')
            if len(tag) > 2:
                tags.add(tag)
        for ent in doc.ents:
            tag = ent.text.replace(' ', '-')
            if len(tag) > 2:
                tags.add(tag)
        return list(tags)
    except Exception as e:
        logging.error(f"Error extracting tags from review: {e}")
        return []

# Analyze sentiment of a review text
def analyze_sentiment(review_text):
    try:
        analyzer = SentimentIntensityAnalyzer()
        if review_text:
            score = analyzer.polarity_scores(review_text)
            compound = score['compound']
            sentiment = 'Positive' if compound >= 0.05 else 'Negative' if compound <= -0.05 else 'Neutral'
            return sentiment, compound
        return 'Neutral', 0.0
    except Exception as e:
        logging.error(f"Error analyzing sentiment: {e}")
        return 'Neutral', 0.0
