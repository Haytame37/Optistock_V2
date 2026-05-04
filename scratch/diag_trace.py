import sys
sys.path.insert(0, '.')
from utils.db import DB_PATH
import sqlite3

conn = sqlite3.connect(DB_PATH, timeout=30)
conn.execute("PRAGMA journal_mode = WAL")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=== IoT data for ENT_DEMO ===")
cursor.execute("""
    SELECT 
        AVG((temp_sensor_1+temp_sensor_2+temp_sensor_3)/3.0) as avg_temp,
        AVG((hum_sensor_1+hum_sensor_2+hum_sensor_3)/3.0) as avg_hum,
        COUNT(*) as n
    FROM iot_readings WHERE warehouse_id='ENT_DEMO'
""")
r = cursor.fetchone()
print(f"  avg_temp={r['avg_temp']:.2f}, avg_hum={r['avg_hum']:.2f}, n={r['n']}")

conn.close()

# Test get_compliant_warehouses directly
from core.iot_filter import get_compliant_warehouses
from utils.product_conditions import PRODUCT_CONDITIONS

print("\n=== Test get_compliant_warehouses ===")
for product in list(PRODUCT_CONDITIONS.keys())[:5]:
    results = get_compliant_warehouses(product, researcher_id=8)
    print(f"  Produit: {product} -> {len(results)} entrepots conformes")
    for w in results:
        print(f"    id={w['id']}, owner_id={w['owner_id']}, nom={w['nom']}, score={w['score_logistique']}")

# Test direct insert into contact_requests
print("\n=== Test insertion directe create_contact_request ===")
from core.messaging import create_contact_request, ensure_messaging_schema
ensure_messaging_schema()
ok, payload = create_contact_request(
    warehouse_id='ENT_DEMO',
    owner_id=7,
    researcher_id=8,
    product_name='Test',
    message='Test message diagnostic'
)
print(f"  ok={ok}, payload={payload}")

# Vérifier
conn2 = sqlite3.connect(DB_PATH, timeout=30)
conn2.execute("PRAGMA journal_mode = WAL")
conn2.row_factory = sqlite3.Row
c2 = conn2.cursor()
c2.execute("SELECT * FROM contact_requests")
rows = c2.fetchall()
print(f"\n  contact_requests apres test: {len(rows)} ligne(s)")
for r in rows:
    print("  ", dict(r))
    # Nettoyer
    c2.execute("DELETE FROM contact_requests WHERE request_id=?", (r['request_id'],))
conn2.commit()
conn2.close()
print("  (nettoyage effectue)")
