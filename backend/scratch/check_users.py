import sqlite3
import os

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database", "optistock.db"))

def list_users():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT user_id, email, role, is_active FROM users")
        users = cursor.fetchall()
        print(f"Total users: {len(users)}")
        for u in users:
            print(f"ID: {u[0]} | Email: {u[1]} | Role: {u[2]} | Active: {u[3]}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    list_users()
