import sqlite3
import os

DB_PATH = "backend/database/optistock.db"

def fix_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # On ajoute la colonne si elle n'existe pas
        cursor.execute("ALTER TABLE warehouses ADD COLUMN iot_token TEXT")
        print("Colonne 'iot_token' ajoutée avec succès.")
    except sqlite3.OperationalError:
        print("La colonne 'iot_token' existe déjà.")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    fix_db()
