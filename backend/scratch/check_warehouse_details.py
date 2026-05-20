import sqlite3
import os

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database", "optistock.db"))

def check_details():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        print("=== USERS ===")
        cursor.execute("SELECT user_id, first_name, last_name, email, role, is_active FROM users")
        for u in cursor.fetchall():
            print(f"ID: {u[0]} | Name: {u[1]} {u[2]} | Email: {u[3]} | Role: {u[4]} | Active: {u[5]}")
            
        print("\n=== WAREHOUSES ===")
        cursor.execute("SELECT warehouse_id, name, owner_id, status, iot_token FROM warehouses")
        for w in cursor.fetchall():
            print(f"ID: {w[0]} | Name: {w[1]} | Owner ID: {w[2]} | Status: {w[3]} | Token: {w[4]}")
            
        print("\n=== MY WAREHOUSE (RESEARCHER LEASES) ===")
        cursor.execute("SELECT id_entrepot, nom, researcher_id, product_name FROM my_warehouse")
        for mw in cursor.fetchall():
            print(f"Warehouse ID: {mw[0]} | Name: {mw[1]} | Researcher ID: {mw[2]} | Product: {mw[3]}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_details()
