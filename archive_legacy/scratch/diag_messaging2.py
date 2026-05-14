import sys, sqlite3
sys.path.insert(0, '.')
from utils.db import DB_PATH

conn = sqlite3.connect(DB_PATH, timeout=30)
conn.execute("PRAGMA journal_mode = WAL")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=== ENTREPOTS avec données IoT ===")
cursor.execute("""
    SELECT w.warehouse_id, w.owner_id, w.name, w.status, COUNT(i.reading_id) as iot_count
    FROM warehouses w
    LEFT JOIN iot_readings i ON i.warehouse_id = w.warehouse_id
    GROUP BY w.warehouse_id
    ORDER BY iot_count DESC
""")
for r in cursor.fetchall():
    print(f"  {r['warehouse_id']} | owner_id={r['owner_id']} | {r['name']} | status={r['status']} | IoT={r['iot_count']}")

print("\n=== Tester insertion contact_request manuellement ===")
try:
    # Simuler une demande: researcher_id=8 (test@gmail.com), warehouse ENT_DEMO, owner_id=7
    cursor.execute("""
        INSERT INTO contact_requests (request_id, warehouse_id, owner_id, researcher_id, product_name, message, status)
        VALUES ('TEST001', 'ENT_DEMO', 7, 8, 'Tomates', 'Test message', 'pending')
    """)
    conn.commit()
    print("  Insertion reussie avec researcher_id=8, owner_id=7")
    # Nettoyer
    cursor.execute("DELETE FROM contact_requests WHERE request_id='TEST001'")
    conn.commit()
except Exception as e:
    print(f"  ERREUR insertion: {e}")

print("\n=== Verifier les foreign keys ===")
cursor.execute("PRAGMA foreign_keys")
fk = cursor.fetchone()[0]
print(f"  Foreign keys actives: {bool(fk)}")

# Tester avec FK
conn2 = sqlite3.connect(DB_PATH, timeout=30)
conn2.execute("PRAGMA journal_mode = WAL")
conn2.execute("PRAGMA foreign_keys = ON")
cur2 = conn2.cursor()
try:
    cur2.execute("""
        INSERT INTO contact_requests (request_id, warehouse_id, owner_id, researcher_id, product_name, message, status)
        VALUES ('TEST002', 'ENT_DEMO', 7, 8, 'Tomates', 'Test message', 'pending')
    """)
    conn2.commit()
    print("  Insertion avec FK=ON: REUSSIE")
    cur2.execute("DELETE FROM contact_requests WHERE request_id='TEST002'")
    conn2.commit()
except Exception as e:
    print(f"  Insertion avec FK=ON: ECHEC -> {e}")

conn.close()
conn2.close()
