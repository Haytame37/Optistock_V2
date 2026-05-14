import sqlite3
db_path = r'database/optistock.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table, sql in tables:
    print(f"--- {table} ---")
    print(sql)
conn.close()
