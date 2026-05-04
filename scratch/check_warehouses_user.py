import sqlite3
db_path = r'database/optistock.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT user_id, email FROM users WHERE email='rafikinajat1@gmail.com'")
user = cursor.fetchone()
if user:
    u_id = user[0]
    cursor.execute("SELECT COUNT(*) FROM warehouses WHERE owner_id=?", (u_id,))
    print(f"Warehouses for {user[1]} (ID {u_id}): {cursor.fetchone()[0]}")
conn.close()
