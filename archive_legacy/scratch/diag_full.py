import sys, sqlite3
sys.path.insert(0, '.')
from utils.db import DB_PATH

conn = sqlite3.connect(DB_PATH, timeout=30)
conn.execute("PRAGMA journal_mode = WAL")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=== contact_requests ===")
cursor.execute("SELECT * FROM contact_requests")
rows = cursor.fetchall()
if rows:
    for r in rows:
        print(dict(r))
else:
    print("VIDE - aucune demande en base")

print("\n=== users (chercheurs actifs) ===")
cursor.execute("SELECT user_id, email, role, is_active FROM users WHERE role='researcher' AND is_active=1")
for r in cursor.fetchall():
    print(dict(r))

print("\n=== users (proprietaires actifs) ===")
cursor.execute("SELECT user_id, email, role, is_active FROM users WHERE role='owner' AND is_active=1")
for r in cursor.fetchall():
    print(dict(r))

print("\n=== warehouses ===")
cursor.execute("SELECT warehouse_id, owner_id, name, status FROM warehouses")
for r in cursor.fetchall():
    print(dict(r))

print("\n=== iot_readings (count par entrepot) ===")
cursor.execute("SELECT warehouse_id, COUNT(*) as n FROM iot_readings GROUP BY warehouse_id")
for r in cursor.fetchall():
    print(dict(r))

conn.close()
