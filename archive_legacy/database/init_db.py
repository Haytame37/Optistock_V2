import sqlite3
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "optistock.db"))

def create_database():
    """Crée ou réinitialise la base de données avec le nouveau schéma EARSER."""
    
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            print("Ancienne base de donnees supprimee.")
        except PermissionError:
            print("Impossible de supprimer le fichier (verrouille). Nettoyage des tables existantes...")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Activer les contraintes de clés étrangères
    cursor.execute("PRAGMA foreign_keys = OFF;")
    
    # Nettoyage
    cursor.execute("DROP TABLE IF EXISTS iot_readings")
    cursor.execute("DROP TABLE IF EXISTS reservations")
    cursor.execute("DROP TABLE IF EXISTS my_warehouse")
    cursor.execute("DROP TABLE IF EXISTS delivery_points")
    cursor.execute("DROP TABLE IF EXISTS warehouses")
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("DROP TABLE IF EXISTS search_history")
    
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Table users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL CHECK(role IN ('admin', 'researcher', 'owner')),
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            is_active INTEGER DEFAULT 1 CHECK(is_active IN (0, 1)),
            created_at DATETIME DEFAULT (datetime('now', '+1 hours')),
            updated_at DATETIME DEFAULT (datetime('now', '+1 hours'))
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
            status TEXT DEFAULT 'available' CHECK(status IN ('available', 'unavailable')),
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

    # 4. Table my_warehouse (Pour les imports chercheurs)
    cursor.execute("DROP TABLE IF EXISTS my_warehouse")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS my_warehouse (
            id_entrepot TEXT PRIMARY KEY,
            researcher_id INTEGER,
            nom TEXT,
            adresse TEXT,
            latitude REAL,
            longitude REAL,
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
            hum_sensor_3 REAL,
            FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id) ON DELETE CASCADE
        )
    ''')

    # Création d'index pour optimiser les jointures et recherches temporelles
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_iot_warehouse ON iot_readings(warehouse_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_iot_recorded_at ON iot_readings(recorded_at);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_res_warehouse ON reservations(warehouse_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_wh_status ON warehouses(status);")

    conn.commit()
    conn.close()
    
    print(f"Base de données SQLite (Schéma EARSER) créée avec succès : {DB_PATH}")

if __name__ == "__main__":
    create_database()
