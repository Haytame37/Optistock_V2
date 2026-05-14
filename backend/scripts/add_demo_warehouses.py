"""
Script pour ajouter des entrepots demo avec donnees IoT variees
couvrant plusieurs types de produits.
"""
import sys, os, sqlite3, random, uuid
from datetime import datetime, timedelta

# Add backend directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import DB_PATH
from utils.product_conditions import PRODUCT_CONDITIONS

conn = sqlite3.connect(DB_PATH, timeout=30)
conn.execute("PRAGMA journal_mode = WAL")
conn.execute("PRAGMA foreign_keys = OFF")
cursor = conn.cursor()

# Les conditions par produit -> on cree un entrepot par categorie de temperature
# ENT_DEMO : temp ~10°C, hum ~65%  -> Parapharmacie, Materiaux
# ENT_FRIGO: temp ~4°C, hum ~80%   -> Produits Laitiers, Produits de la Mer, Viandes
# ENT_CLIM:  temp ~20°C, hum ~50%  -> Tomates, Fleurs, Fruits
# ENT_SEC:   temp ~25°C, hum ~40%  -> Electronique, Textiles
# ENT_AMBI:  temp ~18°C, hum ~55%  -> General

OWNER_ID = 7  # atmansalah019@gmail.com

new_warehouses = [
    {"id": "ENT_FRIGO", "name": "Entrepot Frigorifique",   "address": "Zone Frigo, Casablanca", "lat": 33.58, "lon": -7.62, "vol": 3000, "temp_min": 2,  "temp_max": 6,  "hum_min": 75, "hum_max": 85},
    {"id": "ENT_CLIM",  "name": "Entrepot Climatise",      "address": "Zone Agro, Rabat",       "lat": 34.02, "lon": -6.83, "vol": 5000, "temp_min": 15, "temp_max": 22, "hum_min": 60, "hum_max": 70},
    {"id": "ENT_SEC",   "name": "Entrepot Sec Electronique","address": "Zone Indus, Fes",        "lat": 34.03, "lon": -5.00, "vol": 2000, "temp_min": 20, "temp_max": 26, "hum_min": 35, "hum_max": 45},
    {"id": "ENT_AMBI",  "name": "Entrepot Ambiant",        "address": "Zone Log, Marrakech",    "lat": 31.63, "lon": -8.00, "vol": 8000, "temp_min": 16, "temp_max": 22, "hum_min": 50, "hum_max": 60},
]

now = datetime.now()
added_wh = 0
added_iot = 0

for wh in new_warehouses:
    # Verifier si existe deja
    cursor.execute("SELECT warehouse_id FROM warehouses WHERE warehouse_id=?", (wh["id"],))
    if cursor.fetchone():
        print(f"  {wh['id']} existe deja, skip")
        continue

    cursor.execute("""
        INSERT INTO warehouses (warehouse_id, owner_id, name, address, volume_m3, latitude, longitude, status, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'available', datetime('now','+1 hours'))
    """, (wh["id"], OWNER_ID, wh["name"], wh["address"], wh["vol"], wh["lat"], wh["lon"]))
    added_wh += 1

    # Generer 200 lectures IoT realistes
    records = []
    for i in range(200):
        ts = (now - timedelta(hours=200-i)).strftime("%Y-%m-%d %H:%M:%S")
        temp = round(random.uniform(wh["temp_min"], wh["temp_max"]), 2)
        hum  = round(random.uniform(wh["hum_min"],  wh["hum_max"]),  2)
        # Legere variation entre capteurs
        records.append((
            wh["id"], ts,
            temp, temp + round(random.uniform(-0.5, 0.5), 2), temp + round(random.uniform(-0.5, 0.5), 2),
            hum,  hum  + round(random.uniform(-2, 2), 2),    hum  + round(random.uniform(-2, 2), 2),
        ))

    cursor.executemany("""
        INSERT INTO iot_readings (warehouse_id, recorded_at,
            temp_sensor_1, temp_sensor_2, temp_sensor_3,
            hum_sensor_1,  hum_sensor_2,  hum_sensor_3)
        VALUES (?,?,?,?,?,?,?,?)
    """, records)
    added_iot += len(records)
    print(f"  {wh['id']} ajoute avec {len(records)} lectures IoT (temp={wh['temp_min']}-{wh['temp_max']}°C, hum={wh['hum_min']}-{wh['hum_max']}%)")

conn.commit()
conn.execute("PRAGMA foreign_keys = ON")
conn.close()

print(f"\nTotal: {added_wh} entrepots et {added_iot} lectures IoT ajoutes.")

# Verifier les resultats
print("\n=== Verification get_compliant_warehouses par produit ===")
from core.iot_filter import get_compliant_warehouses
for product in list(PRODUCT_CONDITIONS.keys()):
    results = get_compliant_warehouses(product)
    if results:
        print(f"  {product}: {len(results)} entrepot(s) -> {[r['id'] for r in results]}")
    else:
        print(f"  {product}: aucun entrepot conforme")
