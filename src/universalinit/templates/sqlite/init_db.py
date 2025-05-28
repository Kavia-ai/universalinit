#!/usr/bin/env python3
"""Initialize SQLite database for {KAVIA_TEMPLATE_PROJECT_NAME}"""

import sqlite3
import os

DB_NAME = "{KAVIA_DB_NAME}"

# Create database with sample table
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS app_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT UNIQUE NOT NULL,
        value TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Insert initial data
cursor.execute("INSERT OR REPLACE INTO app_info (key, value) VALUES (?, ?)", 
               ("project_name", "{KAVIA_TEMPLATE_PROJECT_NAME}"))
cursor.execute("INSERT OR REPLACE INTO app_info (key, value) VALUES (?, ?)", 
               ("version", "{KAVIA_PROJECT_VERSION}"))

conn.commit()
conn.close()

print(f"SQLite database created: {DB_NAME}")
