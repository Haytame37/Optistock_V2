import sqlite3
conn = sqlite3.connect('database/optistock.db')
cursor = conn.cursor()
cursor.execute("SELECT reservation_id, status FROM reservations WHERE warehouse_id = 'ENT_DEMO'")
print(cursor.fetchall())
conn.close()
