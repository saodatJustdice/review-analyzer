from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime

def scheduled_review_fetch():
    app_id = "com.google.android.apps.youtube"
    print(f"Fetching reviews at {datetime.now()}")
    reviews_data = fetch_reviews(app_id, count=100)
    save_reviews_to_db(reviews_data, app_id)
    print(f"Saved {len(reviews_data)} reviews.")

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(scheduled_review_fetch, 'interval', days=1, start_date='2025-04-25 00:00:00')
    print("Scheduler started. Press Ctrl+C to stop.")
    scheduler.start()
