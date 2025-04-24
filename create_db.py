import sqlite3  # Built-in module, like requiring 'fs' in Node.js

def create_database():
    try:
        # Connect to SQLite database (creates 'reviews.db' if it doesn't exist)
        conn = sqlite3.connect('reviews.db')
        cursor = conn.cursor()

        # Create the reviews table
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS reviews (
                                                              review_id TEXT PRIMARY KEY,
                                                              app_id TEXT,
                                                              username TEXT,
                                                              rating INTEGER,
                                                              review_text TEXT,
                                                              date TEXT,
                                                              app_version TEXT
                       )
                       ''')

        # Commit changes (like saving a file)
        conn.commit()
        print("Database and reviews table created successfully.")

    except sqlite3.Error as e:
        print(f"Error creating database: {e}")

    finally:
        # Close the connection (like closing a file stream in Node.js)
        conn.close()

if __name__ == "__main__":
    create_database()
