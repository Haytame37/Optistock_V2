import sqlite3
db_path = r'database/optistock.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT email, role, is_active, created_at, datetime('now', '+1 hours') as now FROM users")
users = cursor.fetchall()
for u in users:
    print(u)
conn.close()
