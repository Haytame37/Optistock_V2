import sqlite3
import os

DB_PATH = "backend/database/optistock.db"

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE warehouses ADD COLUMN iot_token TEXT")
        # On met le token actuel par défaut pour les entrepôts existants (ENT001)
        cursor.execute("UPDATE warehouses SET iot_token = 'A5nfCs8VOOzz97F0sD4h' WHERE warehouse_id = 'ENT001'")
        conn.commit()
        print("Migration réussie : Colonne 'iot_token' ajoutée.")
    except Exception as e:
        print(f"La colonne existe peut-être déjà : {e}")
    conn.close()

if __name__ == "__main__":
    migrate()
