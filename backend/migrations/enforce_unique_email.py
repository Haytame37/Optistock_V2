import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "optistock.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    print("Début de la migration : Unicité de l'email...")
    
    # 1. Créer une table temporaire pour stocker les données uniques
    cursor.execute("CREATE TABLE users_temp AS SELECT * FROM users GROUP BY email")
    
    # 2. Supprimer l'ancienne table
    cursor.execute("DROP TABLE users")
    
    # 3. Créer la nouvelle table avec la contrainte UNIQUE
    cursor.execute("""
    CREATE TABLE users (
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
    """)
    
    # 4. Réinsérer les données depuis la table temporaire
    cursor.execute("""
    INSERT INTO users (user_id, role, first_name, last_name, email, password_hash, is_active, created_at, updated_at, otp_code, otp_expiry)
    SELECT user_id, role, first_name, last_name, email, password_hash, is_active, created_at, updated_at, otp_code, otp_expiry
    FROM users_temp
    """)
    
    # 5. Supprimer la table temporaire
    cursor.execute("DROP TABLE users_temp")
    
    conn.commit()
    print("SUCCESS: Migration réussie : L'email est désormais unique et les doublons ont été supprimés.")

except Exception as e:
    conn.rollback()
    print(f"FAILED: Erreur lors de la migration : {e}")
finally:
    conn.close()
