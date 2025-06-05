#!/usr/bin/env python3
"""Initialize SQLite database for {KAVIA_TEMPLATE_PROJECT_NAME}"""

import sqlite3
import os

DB_NAME = "{KAVIA_DB_NAME}"
DB_USER = "{KAVIA_DB_USER}"  # Not used for SQLite, but kept for consistency
DB_PASSWORD = "{KAVIA_DB_PASSWORD}"  # Not used for SQLite, but kept for consistency
DB_PORT = "{KAVIA_DB_PORT}"  # Not used for SQLite, but kept for consistency

print("Starting SQLite setup...")

# Check if database already exists
db_exists = os.path.exists(DB_NAME)
if db_exists:
    print(f"SQLite database already exists at {DB_NAME}")
else:
    print("Creating new SQLite database...")

# Create database with sample tables
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Create initial schema
cursor.execute("""
    CREATE TABLE IF NOT EXISTS app_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT UNIQUE NOT NULL,
        value TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Create a sample users table as an example
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Insert initial data
cursor.execute("INSERT OR REPLACE INTO app_info (key, value) VALUES (?, ?)", 
               ("project_name", "{KAVIA_TEMPLATE_PROJECT_NAME}"))
cursor.execute("INSERT OR REPLACE INTO app_info (key, value) VALUES (?, ?)", 
               ("version", "{KAVIA_PROJECT_VERSION}"))
cursor.execute("INSERT OR REPLACE INTO app_info (key, value) VALUES (?, ?)", 
               ("author", "{KAVIA_PROJECT_AUTHOR}"))
cursor.execute("INSERT OR REPLACE INTO app_info (key, value) VALUES (?, ?)", 
               ("description", "{KAVIA_PROJECT_DESCRIPTION}"))

conn.commit()

# Get database statistics
cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
table_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM app_info")
record_count = cursor.fetchone()[0]

conn.close()

# Save connection information to a file
current_dir = os.getcwd()
connection_string = f"sqlite:///{current_dir}/{DB_NAME}"

with open("db_connection.txt", "w") as f:
    f.write(f"# SQLite connection methods:\n")
    f.write(f"# Python: sqlite3.connect('{DB_NAME}')\n")
    f.write(f"# Connection string: {connection_string}\n")
    f.write(f"# File path: {current_dir}/{DB_NAME}\n")

print("Connection information saved to db_connection.txt")

print("\nSQLite setup complete!")
print(f"Database: {DB_NAME}")
print(f"Location: {current_dir}/{DB_NAME}")
print("")

print("To connect to the database, use one of the following methods:")
print(f"1. Python: sqlite3.connect('{DB_NAME}')")
print(f"2. Connection string: {connection_string}")
print(f"3. Direct file access: {current_dir}/{DB_NAME}")
print("")

print("Database statistics:")
print(f"  Tables: {table_count}")
print(f"  App info records: {record_count}")

# If sqlite3 CLI is available, show how to use it
try:
    import subprocess
    result = subprocess.run(['which', 'sqlite3'], capture_output=True, text=True)
    if result.returncode == 0:
        print("")
        print("SQLite CLI is available. You can also use:")
        print(f"  sqlite3 {DB_NAME}")
except:
    pass
