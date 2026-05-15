import sqlite3
import os

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database", "optistock.db"))

def migrate():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("Adding 'demand' column to delivery_points table...")
        # Check if column exists
        cursor.execute("PRAGMA table_info(delivery_points)")
        columns = [c[1] for c in cursor.fetchall()]
        
        if 'demand' not in columns:
            cursor.execute("ALTER TABLE delivery_points ADD COLUMN demand REAL DEFAULT 1.0")
            print("Column 'demand' added successfully.")
        else:
            print("Column 'demand' already exists.")
            
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
