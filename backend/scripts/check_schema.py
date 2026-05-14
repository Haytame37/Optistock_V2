import sqlite3
import os

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database', 'optistock.db'))
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='delivery_points';")
    schema = cursor.fetchone()
    if schema:
        print(schema[0])
    else:
        print("Table delivery_points not found.")
    conn.close()
else:
    print(f"Database not found at {db_path}")
