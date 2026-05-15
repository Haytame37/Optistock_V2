import sqlite3
import os

DB_PATH = "backend/database/optistock.db"

def check_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(warehouses)")
    columns = cursor.fetchall()
    for col in columns:
        print(col)
    conn.close()

if __name__ == "__main__":
    check_schema()
