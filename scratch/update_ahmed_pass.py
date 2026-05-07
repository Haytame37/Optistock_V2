import sqlite3
import bcrypt

conn = sqlite3.connect('database/optistock.db')
hashed = bcrypt.hashpw(b'123456', bcrypt.gensalt()).decode()
conn.execute("UPDATE users SET password_hash=? WHERE email='ahmed@gmail.com'", (hashed,))
conn.commit()
print("Password updated successfully for ahmed@gmail.com to '123456'")
