import sqlite3
import os

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database", "optistock.db"))

def run_migration():
    if not os.path.exists(db_path):
        print(f"ERREUR : La base de données n'a pas été trouvée à {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print(f"Vérification de la table search_history : {db_path}")
        
        cursor.execute("PRAGMA table_info(search_history)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if not columns:
            print("ERREUR : La table 'search_history' n'existe pas.")
            return

        if "cost_weight" not in columns:
            print("Ajout de la colonne 'cost_weight'...")
            cursor.execute("ALTER TABLE search_history ADD COLUMN cost_weight REAL DEFAULT 0.5")
        
        if "dist_weight" not in columns:
            print("Ajout de la colonne 'dist_weight'...")
            cursor.execute("ALTER TABLE search_history ADD COLUMN dist_weight REAL DEFAULT 0.5")

        conn.commit()
        print("SUCCESS : Migration search_history terminée avec succès.")
        
    except Exception as e:
        conn.rollback()
        print(f"FAILED : Erreur lors de la migration : {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
