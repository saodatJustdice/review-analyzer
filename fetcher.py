from google_play_scraper import reviews, Sort
import logging
import time

# Fetch reviews with pagination, with a callback for UI updates
def fetch_all_reviews(app_id, batch_size=100, delay=10, max_retries=3, update_ui=None):
    all_reviews = []
    continuation_token = None
    total_fetched = 0

    try:
        message = "Starting review fetch..."
        logging.info(message)
        if update_ui:
            update_ui(message)

        while True:
            retries = 0
            while retries < max_retries:
                try:
                    result, continuation_token = reviews(
                        app_id,
                        lang='en',
                        country='us',
                        sort=Sort.NEWEST,
                        count=batch_size,
                        continuation_token=continuation_token
                    )
                    all_reviews.extend(result)
                    total_fetched += len(result)
                    message = f"Fetched batch of {len(result)} reviews. Total: {total_fetched}"
                    logging.info(message)
                    if update_ui:
                        update_ui(message)
                    break
                except Exception as e:
                    retries += 1
                    message = f"Error fetching batch (attempt {retries}/{max_retries}): {e}"
                    logging.warning(message)
                    if update_ui:
                        update_ui(message)
                    if retries == max_retries:
                        message = "Max retries reached. Skipping batch."
                        logging.error(message)
                        if update_ui:
                            update_ui(message)
                        break
                    time.sleep(delay * retries)
            if not result or continuation_token is None:
                message = "No more reviews to fetch."
                logging.info(message)
                if update_ui:
                    update_ui(message)
                break
            time.sleep(delay)
    except Exception as e:
        message = f"Error fetching reviews: {e}"
        logging.error(message)
        if update_ui:
            update_ui(message)
        return all_reviews

    return all_reviews
