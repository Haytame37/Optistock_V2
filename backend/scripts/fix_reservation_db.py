import sqlite3
import os

DB_PATH = "backend/database/optistock.db"

def fix_reservation_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Créer la table reservations si elle n'existe pas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            reservation_id TEXT PRIMARY KEY,
            warehouse_id TEXT NOT NULL,
            researcher_id INTEGER NOT NULL,
            global_score REAL,
            status TEXT DEFAULT 'pending',
            reason TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id),
            FOREIGN KEY (researcher_id) REFERENCES users(user_id)
        )
    """)

    # 2. Créer la table my_warehouse si elle n'existe pas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS my_warehouse (
            id_entrepot TEXT PRIMARY KEY,
            researcher_id INTEGER NOT NULL,
            nom TEXT,
            adresse TEXT,
            latitude REAL,
            longitude REAL,
            iot_token TEXT,
            FOREIGN KEY (id_entrepot) REFERENCES warehouses(warehouse_id),
            FOREIGN KEY (researcher_id) REFERENCES users(user_id)
        )
    """)
    
    conn.commit()
    conn.close()
    print("Tables de réservation et d'actifs prêtes.")

if __name__ == "__main__":
    fix_reservation_tables()
