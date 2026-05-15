import sqlite3
import os
import bcrypt

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database", "optistock.db"))

def seed():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    password = "password123"
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    users = [
        ('admin', 'Admin', 'Optistock', 'admin@optistock.ma', hashed),
        ('researcher', 'Najat', 'Chercheur', 'najat@optistock.ma', hashed),
        ('owner', 'Amine', 'Proprio', 'amine@optistock.ma', hashed),
    ]
    
    try:
        print("Seeding users...")
        for role, fname, lname, email, pwd in users:
            # Check if exists
            cursor.execute("SELECT 1 FROM users WHERE email = ?", (email,))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO users (role, first_name, last_name, email, password_hash)
                    VALUES (?, ?, ?, ?, ?)
                """, (role, fname, lname, email, pwd))
                print(f"User {email} created.")
            else:
                print(f"User {email} already exists.")
        
        print("Seeding complete.")
    except Exception as e:
        print(f"Error seeding users: {e}")
    finally:
        conn.close()

def seed_warehouses():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # On récupère l'ID du premier proprio (Amine)
    cursor.execute("SELECT user_id FROM users WHERE email = 'amine@optistock.ma'")
    owner_row = cursor.fetchone()
    if not owner_row:
        print("Owner not found, skip warehouse seeding.")
        return
    owner_id = owner_row[0]
    
    warehouses = [
        ('WH001', owner_id, 'Atlas Cold Storage', 'Béni Mellal, Zone Industrielle', 2500, 32.337, -6.35, 'IOT_WH001_TOKEN', 'froid', 'available'),
        ('WH002', owner_id, 'Casablanca Logistics Hub', 'Casablanca, Ain Sebaa', 5000, 33.6, -7.5, 'IOT_WH002_TOKEN', 'standard', 'available'),
        ('WH003', owner_id, 'Marrakech Fresh Center', 'Marrakech, Route de Safi', 1800, 31.63, -8.0, 'IOT_WH003_TOKEN', 'pharmaceutique', 'available'),
        ('WH004', owner_id, 'Fès North Depot', 'Fès, Quartier Industrielle', 3200, 34.03, -5.0, 'IOT_WH004_TOKEN', 'standard', 'available'),
    ]
    
    try:
        print("Seeding warehouses...")
        for wid, oid, name, addr, vol, lat, lon, token, stype, status in warehouses:
            cursor.execute("SELECT 1 FROM warehouses WHERE warehouse_id = ?", (wid,))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO warehouses (warehouse_id, owner_id, name, address, volume_m3, latitude, longitude, iot_token, storage_type, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (wid, oid, name, addr, vol, lat, lon, token, stype, status))
                print(f"Warehouse {wid} created.")
        conn.commit()
        print("Warehouse seeding complete.")
    except Exception as e:
        print(f"Error seeding warehouses: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    seed()
    seed_warehouses()
