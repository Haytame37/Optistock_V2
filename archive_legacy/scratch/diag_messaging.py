import sys, sqlite3
sys.path.insert(0, '.')
from utils.db import DB_PATH

conn = sqlite3.connect(DB_PATH, timeout=30)
conn.execute("PRAGMA journal_mode = WAL")
cursor = conn.cursor()

print("=== TABLES EXISTANTES ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [r[0] for r in cursor.fetchall()]
print(tables)

print("\n=== contact_requests ===")
if 'contact_requests' in tables:
    cursor.execute("SELECT * FROM contact_requests LIMIT 10")
    rows = cursor.fetchall()
    if rows:
        cursor.execute("PRAGMA table_info(contact_requests)")
        cols = [c[1] for c in cursor.fetchall()]
        print("Colonnes:", cols)
        for r in rows:
            print(dict(zip(cols, r)))
    else:
        print("Table vide - aucune demande enregistree")
else:
    print("Table contact_requests INEXISTANTE !")

print("\n=== warehouses (owner_id) ===")
cursor.execute("SELECT warehouse_id, owner_id, name FROM warehouses LIMIT 5")
for r in cursor.fetchall():
    print(f"  {r[0]} | owner_id={r[1]} | {r[2]}")

print("\n=== users (owners) ===")
cursor.execute("SELECT user_id, email, role, is_active FROM users WHERE role='owner' AND is_active=1")
for r in cursor.fetchall():
    print(f"  user_id={r[0]} | {r[1]} | {r[2]}")

conn.close()
