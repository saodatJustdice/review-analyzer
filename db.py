import sqlite3
import pandas as pd
import logging
import streamlit as st
from config import DB_PATH, DEFAULT_TAGS
import time

# Global flag to ensure init_db is called only once
_DB_INITIALIZED = False

# Initialize database tables
def init_db():
    global _DB_INITIALIZED
    if _DB_INITIALIZED:
        logging.info("Database already initialized, skipping init_db.")
        return
    try:
        start_time = time.time()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Reviews table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                app_id TEXT,
                review_id TEXT PRIMARY KEY,
                username TEXT,
                date TEXT,
                rating INTEGER,
                review_text TEXT,
                sentiment TEXT,
                sentiment_score FLOAT,
                tags TEXT
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_app_id ON reviews (app_id)')

        # App IDs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_ids (
                app_id TEXT PRIMARY KEY
            )
        ''')

        # Tag rules table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tag_rules'")
        if cursor.fetchone():
            cursor.execute("PRAGMA table_info(tag_rules)")
            columns = [info[1] for info in cursor.fetchall()]
            if 'app_id' not in columns:
                logging.info("Migrating tag_rules table to include app_id column.")
                cursor.execute("ALTER TABLE tag_rules RENAME TO tag_rules_old")
                cursor.execute('''
                    CREATE TABLE tag_rules (
                        app_id TEXT,
                        tag_name TEXT,
                        keywords TEXT,
                        PRIMARY KEY (app_id, tag_name)
                    )
                ''')
                cursor.execute("INSERT INTO tag_rules (app_id, tag_name, keywords) SELECT 'cashgiraffe.app', tag_name, keywords FROM tag_rules_old")
                cursor.execute("DROP TABLE tag_rules_old")
                logging.info("tag_rules table migration completed.")
        else:
            cursor.execute('''
                CREATE TABLE tag_rules (
                    app_id TEXT,
                    tag_name TEXT,
                    keywords TEXT,
                    PRIMARY KEY (app_id, tag_name)
                )
            ''')

        # Extracted tags table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS extracted_tags (
                app_id TEXT,
                tag_name TEXT,
                PRIMARY KEY (app_id, tag_name)
            )
        ''')

        # Populate app_ids with initial values if empty
        cursor.execute("SELECT COUNT(*) FROM app_ids")
        if cursor.fetchone()[0] == 0:
            initial_app_ids = ['cashgiraffe.app', 'com.whatsapp']
            for app_id in initial_app_ids:
                cursor.execute("INSERT INTO app_ids (app_id) VALUES (?)", (app_id,))

        # Populate tag_rules with default tags for apps that don't have tag rules
        cursor.execute("SELECT app_id FROM app_ids")
        app_ids = [row[0] for row in cursor.fetchall()]
        for app_id in app_ids:
            cursor.execute("SELECT COUNT(*) FROM tag_rules WHERE app_id = ?", (app_id,))
            if cursor.fetchone()[0] == 0 and app_id in DEFAULT_TAGS:
                for tag_name, keywords in DEFAULT_TAGS[app_id].items():
                    cursor.execute("INSERT INTO tag_rules (app_id, tag_name, keywords) VALUES (?, ?, ?)",
                                   (app_id, tag_name, ','.join(keywords)))

        conn.commit()
        conn.close()
        _DB_INITIALIZED = True
        logging.info(f"Database initialized successfully at {DB_PATH}.")
        logging.info(f"init_db took {time.time() - start_time:.2f} seconds")
    except Exception as e:
        logging.error(f"Error initializing database: {e}")
        raise

# Fetch all app IDs from the database
def get_app_ids():
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT app_id FROM app_ids")
        app_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        return sorted(app_ids)
    except Exception as e:
        logging.error(f"Error fetching app IDs: {e}")
        return ['cashgiraffe.app', 'com.whatsapp']

# Add a new app ID to the database
def add_app_id(new_app_id):
    try:
        init_db()
        new_app_id = new_app_id.strip()
        if not new_app_id or ' ' in new_app_id:
            raise ValueError("App ID must be non-empty and contain no spaces.")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO app_ids (app_id) VALUES (?)", (new_app_id,))
        conn.commit()
        conn.close()
        logging.info(f"Added new app ID: {new_app_id}")
        get_reviews.clear()
    except Exception as e:
        logging.error(f"Error adding app ID {new_app_id}: {e}")
        raise

# Load tag rules from the database for a specific app
def load_tag_rules(app_id='cashgiraffe.app'):
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT tag_name, keywords FROM tag_rules WHERE app_id = ?", (app_id,))
        tag_rules = {}
        for tag_name, keywords in cursor.fetchall():
            tag_rules[tag_name] = keywords.split(',')
        conn.close()
        return tag_rules
    except Exception as e:
        logging.error(f"Error loading tag rules for {app_id}: {e}")
        return {}

# Load extracted tags from the database for a specific app
def load_extracted_tags(app_id='cashgiraffe.app'):
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT tag_name FROM extracted_tags WHERE app_id = ?", (app_id,))
        extracted_tags = [row[0] for row in cursor.fetchall()]
        conn.close()
        return extracted_tags
    except Exception as e:
        logging.error(f"Error loading extracted tags for {app_id}: {e}")
        return []

# Add a new tag rule
def add_tag_rule(app_id, tag_name, keywords):
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO tag_rules (app_id, tag_name, keywords) VALUES (?, ?, ?)",
                       (app_id, tag_name, ','.join(keywords)))
        conn.commit()
        conn.close()
        logging.info(f"Added tag rule for {app_id}: {tag_name} with keywords {keywords}")
    except Exception as e:
        logging.error(f"Error adding tag rule: {e}")
        raise

# Add an extracted tag
def add_extracted_tag(app_id, tag_name):
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO extracted_tags (app_id, tag_name) VALUES (?, ?)",
                       (app_id, tag_name))
        conn.commit()
        conn.close()
        logging.info(f"Added extracted tag for {app_id}: {tag_name}")
    except Exception as e:
        logging.error(f"Error adding extracted tag: {e}")
        raise

# Delete a tag rule and remove the tag from reviews
def delete_tag_rule(app_id, tag_name):
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT review_id, tags FROM reviews WHERE app_id = ? AND tags LIKE ?",
                       (app_id, f'%{tag_name}%'))
        for review_id, tags in cursor.fetchall():
            if tags:
                tag_list = tags.split(',')
                if tag_name in tag_list:
                    tag_list.remove(tag_name)
                    new_tags = ','.join(tag_list) if tag_list else None
                    cursor.execute("UPDATE reviews SET tags = ? WHERE review_id = ?",
                                   (new_tags, review_id))
        cursor.execute("DELETE FROM tag_rules WHERE app_id = ? AND tag_name = ?", (app_id, tag_name))
        conn.commit()
        conn.close()
        logging.info(f"Deleted tag rule for {app_id}: {tag_name}")
    except Exception as e:
        logging.error(f"Error deleting tag rule: {e}")
        raise

# Delete an extracted tag and remove it from reviews
def delete_extracted_tag(app_id, tag_name):
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT review_id, tags FROM reviews WHERE app_id = ? AND tags LIKE ?",
                       (app_id, f'%{tag_name}%'))
        for review_id, tags in cursor.fetchall():
            if tags:
                tag_list = tags.split(',')
                if tag_name in tag_list:
                    tag_list.remove(tag_name)
                    new_tags = ','.join(tag_list) if tag_list else None
                    cursor.execute("UPDATE reviews SET tags = ? WHERE review_id = ?",
                                   (new_tags, review_id))
        cursor.execute("DELETE FROM extracted_tags WHERE app_id = ? AND tag_name = ?", (app_id, tag_name))
        conn.commit()
        conn.close()
        logging.info(f"Deleted extracted tag for {app_id}: {tag_name}")
    except Exception as e:
        logging.error(f"Error deleting extracted tag: {e}")
        raise

# Database connection (cached)
@st.cache_data
def get_reviews(app_id='cashgiraffe.app', _cache_buster=0):
    try:
        init_db()
        logging.info(f"Fetching reviews for app_id: {app_id}")
        start_time = time.time()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM reviews WHERE app_id = ?", (app_id,))
        count = cursor.fetchone()[0]
        logging.info(f"Found {count} reviews for {app_id} in the database.")

        query = "SELECT * FROM reviews WHERE app_id = ?"
        df = pd.read_sql_query(query, conn, params=(app_id,))
        conn.close()
        logging.info(f"Database query took {time.time() - start_time:.2f} seconds")

        if df.empty:
            logging.info("No reviews found in the database after loading into DataFrame.")
            return pd.DataFrame()

        start_time = time.time()
        df['date'] = pd.to_datetime(df['date'])
        logging.info(f"Date conversion took {time.time() - start_time:.2f} seconds")

        start_time = time.time()
        has_duplicates = df['username'].duplicated().any()
        if has_duplicates:
            df['display_username'] = df.apply(
                lambda x: f"{x['username']} (ID: {x['review_id'][-4:]})", axis=1)
        else:
            df['display_username'] = df['username']
        logging.info(f"Display username calculation took {time.time() - start_time:.2f} seconds")

        logging.info(f"Returning DataFrame with {len(df)} rows for {app_id}.")
        return df
    except Exception as e:
        logging.error(f"Error loading reviews from database: {e}")
        return pd.DataFrame()

# Function to clear the cache for get_reviews
def clear_reviews_cache():
    get_reviews.clear()
