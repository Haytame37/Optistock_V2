import sqlite3
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "database", "optistock.db"))
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Corriger created_at et updated_at dans users (ajouter 1h aux timestamps UTC existants)
cur.execute("""
    UPDATE users
    SET created_at = datetime(created_at, '+1 hours'),
        updated_at = datetime(updated_at, '+1 hours')
""")
print(f'users updated: {cur.rowcount} rows')

# Corriger updated_at dans warehouses
cur.execute("""
    UPDATE warehouses
    SET updated_at = datetime(updated_at, '+1 hours')
    WHERE updated_at IS NOT NULL
""")
print(f'warehouses updated: {cur.rowcount} rows')

# Corriger created_at et updated_at dans reservations
cur.execute("""
    UPDATE reservations
    SET created_at = datetime(created_at, '+1 hours'),
        updated_at = datetime(updated_at, '+1 hours')
    WHERE created_at IS NOT NULL
""")
print(f'reservations updated: {cur.rowcount} rows')

conn.commit()
conn.close()
print('Done - all timestamps corrected to GMT+1')
