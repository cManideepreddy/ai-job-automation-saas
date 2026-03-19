import sqlite3

# Create connection
conn = sqlite3.connect("app.db", check_same_thread=False)
cursor = conn.cursor()

# Create table
cursor.execute("""
               CREATE TABLE IF NOT EXISTS user_activity (
                                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                            email TEXT,
                                                            resume TEXT,
                                                            ats_score INTEGER,
                                                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
               )
               """)

conn.commit()