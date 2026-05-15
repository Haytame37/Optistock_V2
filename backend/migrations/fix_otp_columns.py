import sqlite3
import os

# Définir le chemin de la base de données
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database", "optistock.db"))

def run_migration():
    if not os.path.exists(db_path):
        print(f"ERREUR : La base de données n'a pas été trouvée à {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print(f"Vérification de la base de données : {db_path}")
        
        # Vérifier les colonnes existantes
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if not columns:
            print("ERREUR : La table 'users' n'existe pas.")
            return

        # 1. Ajouter otp_code si manquant
        if "otp_code" not in columns:
            print("Ajout de la colonne 'otp_code'...")
            cursor.execute("ALTER TABLE users ADD COLUMN otp_code TEXT")
        else:
            print("La colonne 'otp_code' existe déjà.")
            
        # 2. Ajouter otp_expiry si manquant
        if "otp_expiry" not in columns:
            print("Ajout de la colonne 'otp_expiry'...")
            cursor.execute("ALTER TABLE users ADD COLUMN otp_expiry TEXT")
        else:
            print("La colonne 'otp_expiry' existe déjà.")

        # 3. Gérer l'unicité de l'email (SQLite ALTER TABLE ne permet pas d'ajouter UNIQUE directement)
        # On vérifie si l'email est déjà unique ou si on doit recréer la table
        # Pour faire simple ici, on se concentre sur les colonnes OTP demandées.
        
        conn.commit()
        print("SUCCESS : Migration terminée avec succès.")
        
    except Exception as e:
        conn.rollback()
        print(f"FAILED : Erreur lors de la migration : {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
