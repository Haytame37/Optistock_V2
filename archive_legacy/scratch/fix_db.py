import sqlite3
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database", "optistock.db"))

def fix_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
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
    
    conn.commit()
    conn.close()
    print("Table 'search_history' créée avec succès !")

if __name__ == "__main__":
    fix_database()
