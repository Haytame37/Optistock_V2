import sqlite3
import os

db_path = r'database/optistock.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    print("--- Début de la mise à jour du schéma (Cascading Deletes) ---")
    
    # 1. Sauvegarder les données des entrepôts
    cursor.execute("SELECT * FROM warehouses")
    warehouses_data = cursor.fetchall()
    
    # Obtenir les colonnes
    cursor.execute("PRAGMA table_info(warehouses)")
    columns = [col[1] for col in cursor.fetchall()]
    cols_str = ",".join(columns)
    placeholders = ",".join(["?"] * len(columns))
    
    # 2. Supprimer l'ancienne table
    # On doit d'abord désactiver les FK pour pouvoir supprimer/recréer
    cursor.execute("PRAGMA foreign_keys = OFF")
    cursor.execute("DROP TABLE warehouses")
    
    # 3. Créer la nouvelle table avec ON DELETE CASCADE
    cursor.execute(f"""
        CREATE TABLE warehouses (
            warehouse_id TEXT PRIMARY KEY,
            owner_id INTEGER,
            name TEXT,
            address TEXT,
            volume_m3 REAL,
            latitude REAL,
            longitude REAL,
            status TEXT DEFAULT 'available' CHECK(status IN ('available', 'unavailable')),
            updated_at DATETIME DEFAULT (datetime('now', '+1 hours')),
            FOREIGN KEY (owner_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)
    
    # 4. Restaurer les données
    cursor.executemany(f"INSERT INTO warehouses ({cols_str}) VALUES ({placeholders})", warehouses_data)
    
    cursor.execute("PRAGMA foreign_keys = ON")
    conn.commit()
    print("✅ Table 'warehouses' mise à jour avec ON DELETE CASCADE.")
    
except Exception as e:
    conn.rollback()
    print(f"❌ Erreur : {e}")
finally:
    conn.close()
