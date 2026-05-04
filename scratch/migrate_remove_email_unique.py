"""
Migration : suppression de la contrainte UNIQUE sur la colonne email de la table users.
Permet la creation de plusieurs comptes avec le meme email (roles differents).
"""
import sqlite3
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.db import DB_PATH

def migrate():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA foreign_keys = OFF")
    cursor = conn.cursor()

    try:
        # 1. Verifier si la contrainte UNIQUE existe deja
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'")
        schema = cursor.fetchone()[0]
        print("Schema actuel :")
        print(schema)

        if "UNIQUE" not in schema.upper() or "email TEXT NOT NULL" in schema and "email TEXT UNIQUE" not in schema:
            print("\nContrainte UNIQUE deja absente. Migration non necessaire.")
            conn.close()
            return

        print("\nMigration en cours...")

        # 2. Creer la nouvelle table sans UNIQUE sur email
        cursor.execute("""
            CREATE TABLE users_new (
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
        """)

        # 3. Copier toutes les donnees
        cursor.execute("""
            INSERT INTO users_new (user_id, role, first_name, last_name, email, password_hash, is_active, created_at, updated_at)
            SELECT user_id, role, first_name, last_name, email, password_hash, is_active, created_at, updated_at
            FROM users
        """)
        copied = cursor.rowcount
        print(f"  {copied} utilisateurs copies.")

        # 4. Supprimer l'ancienne table et renommer
        cursor.execute("DROP TABLE users")
        cursor.execute("ALTER TABLE users_new RENAME TO users")

        # 5. Remettre le compteur AUTOINCREMENT
        cursor.execute("SELECT MAX(user_id) FROM users")
        max_id = cursor.fetchone()[0] or 0
        cursor.execute("UPDATE sqlite_sequence SET seq = ? WHERE name = 'users'", (max_id,))

        # 6. Recreer les index utiles
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active)")

        conn.commit()
        print("  Migration terminee avec succes !")

        # Verification
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'")
        new_schema = cursor.fetchone()[0]
        print("\nNouveau schema :")
        print(new_schema)

    except Exception as e:
        conn.rollback()
        print(f"ERREUR : {e}")
        raise
    finally:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.close()

if __name__ == "__main__":
    migrate()
