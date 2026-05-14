import sqlite3
db_path = r'database/optistock.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT * FROM sqlite_sequence WHERE name='users';")
print(cursor.fetchone())
conn.close()
