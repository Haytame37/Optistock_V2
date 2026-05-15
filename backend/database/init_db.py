import sqlite3
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "optistock.db"))

def create_database():
    """Crée la base de données si elle n'existe pas, sans supprimer les données existantes."""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Activer les contraintes de clés étrangères
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Table users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL CHECK(role IN ('admin', 'researcher', 'owner')),
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            is_active INTEGER DEFAULT 1 CHECK(is_active IN (0, 1)),
            created_at DATETIME DEFAULT (datetime('now', '+1 hours')),
            updated_at DATETIME DEFAULT (datetime('now', '+1 hours')),
            otp_code TEXT,
            otp_expiry TEXT
        )
    ''')

    # 2. Table warehouses
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS warehouses (
            warehouse_id TEXT PRIMARY KEY,
            owner_id INTEGER,
            name TEXT,
            address TEXT,
            volume_m3 REAL,
            latitude REAL,
            longitude REAL,
            iot_token TEXT,
            storage_type TEXT DEFAULT 'standard',
            status TEXT DEFAULT 'available' CHECK(status IN ('available', 'unavailable', 'locked', 'rented')),
            updated_at DATETIME DEFAULT (datetime('now', '+1 hours')),
            FOREIGN KEY (owner_id) REFERENCES users(user_id) ON DELETE SET NULL
        )
    ''')

    # 3. Table delivery_points
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS delivery_points (
            request_id TEXT PRIMARY KEY,
            researcher_id INTEGER,
            name TEXT,
            latitude REAL,
            longitude REAL,
            FOREIGN KEY (researcher_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    ''')

    # 4. Table my_warehouse (Pour les actifs chercheurs)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS my_warehouse (
            id_entrepot TEXT PRIMARY KEY,
            researcher_id INTEGER,
            nom TEXT,
            adresse TEXT,
            latitude REAL,
            longitude REAL,
            iot_token TEXT,
            product_name TEXT,
            FOREIGN KEY (researcher_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    ''')

    # 5. Table reservations
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            reservation_id TEXT PRIMARY KEY,
            warehouse_id TEXT,
            researcher_id INTEGER,
            global_score REAL,
            status TEXT DEFAULT 'pending' CHECK(status IN ('pre_lock', 'pending', 'confirmed', 'canceled')),
            reason TEXT,
            created_at DATETIME DEFAULT (datetime('now', '+1 hours')),
            updated_at DATETIME DEFAULT (datetime('now', '+1 hours')),
            expires_at DATETIME,
            FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id) ON DELETE CASCADE,
            FOREIGN KEY (researcher_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    ''')

    # 6. Table search_history
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            researcher_id INTEGER,
            product_name TEXT,
            volume REAL,
            duration_days INTEGER,
            cost_weight REAL,
            dist_weight REAL,
            results_json TEXT,
            created_at DATETIME DEFAULT (datetime('now', '+1 hours')),
            FOREIGN KEY (researcher_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    ''')

    # 5. Table iot_readings
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS iot_readings (
            reading_id INTEGER PRIMARY KEY AUTOINCREMENT,
            warehouse_id TEXT NOT NULL,
            recorded_at DATETIME NOT NULL,
            temp_sensor_1 REAL,
            temp_sensor_2 REAL,
            temp_sensor_3 REAL,
            hum_sensor_1 REAL,
            hum_sensor_2 REAL,
            hum_sensor_3 REAL
        )
    ''')

    # --- LOGIQUE D'AUTO-RÉPARATION (MIGRATIONS AUTOMATIQUES) ---
    
    # Vérification des colonnes pour warehouses
    cursor.execute("PRAGMA table_info(warehouses)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'iot_token' not in columns:
        cursor.execute("ALTER TABLE warehouses ADD COLUMN iot_token TEXT")
    if 'storage_type' not in columns:
        cursor.execute("ALTER TABLE warehouses ADD COLUMN storage_type TEXT DEFAULT 'standard'")
    
    # Vérification des colonnes pour my_warehouse
    cursor.execute("PRAGMA table_info(my_warehouse)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'iot_token' not in columns:
        cursor.execute("ALTER TABLE my_warehouse ADD COLUMN iot_token TEXT")
    if 'product_name' not in columns:
        cursor.execute("ALTER TABLE my_warehouse ADD COLUMN product_name TEXT")

    conn.commit()
    conn.close()
    
    print(f"Base de données SQLite auto-réparée et prête : {DB_PATH}")

if __name__ == "__main__":
    create_database()
