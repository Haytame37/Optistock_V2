import sqlite3
import os

db_path = r'database/optistock.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users';")
schema = cursor.fetchone()
if schema:
    print(schema[0])
conn.close()
