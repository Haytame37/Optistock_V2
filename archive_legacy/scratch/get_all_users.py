import sqlite3

conn = sqlite3.connect('database/optistock.db')
c = conn.cursor()
c.execute("SELECT email, password_hash FROM users")
for row in c.fetchall():
    print(row)
conn.close()
