import sqlite3

def fix_status_constraint():
    conn = sqlite3.connect('backend/database/optistock.db')
    cursor = conn.cursor()
    
    try:
        # 1. On récupère la structure actuelle
        print("Début de la migration des statuts...")
        
        # On crée une table temporaire avec la nouvelle contrainte (qui accepte locked et rented)
        cursor.execute("""
            CREATE TABLE warehouses_new (
                warehouse_id TEXT PRIMARY KEY,
                owner_id INTEGER,
                name TEXT NOT NULL,
                address TEXT,
                volume_m3 REAL,
                latitude REAL,
                longitude REAL,
                iot_token TEXT,
                storage_type TEXT DEFAULT 'standard',
                status TEXT CHECK(status IN ('available', 'unavailable', 'locked', 'rented')) DEFAULT 'available',
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (owner_id) REFERENCES users(user_id)
            )
        """)
        
        # 2. On copie les données existantes
        cursor.execute("""
            INSERT INTO warehouses_new (warehouse_id, owner_id, name, address, volume_m3, latitude, longitude, iot_token, storage_type, status, updated_at)
            SELECT warehouse_id, owner_id, name, address, volume_m3, latitude, longitude, iot_token, storage_type, status, updated_at 
            FROM warehouses
        """)
        
        # 3. On remplace l'ancienne table par la nouvelle
        cursor.execute("DROP TABLE warehouses")
        cursor.execute("ALTER TABLE warehouses_new RENAME TO warehouses")
        
        conn.commit()
        print("Migration réussie ! Les statuts 'locked' et 'rented' sont maintenant autorisés.")
        
    except Exception as e:
        conn.rollback()
        print(f"Erreur lors de la migration : {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_status_constraint()
