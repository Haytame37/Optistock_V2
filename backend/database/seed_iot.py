import sqlite3
import random
from datetime import datetime, timedelta
import os

# Configuration
DB_PATH = os.path.join(os.path.dirname(__file__), "optistock.db")
WAREHOUSE_ID = "ENT001"

def seed_iot_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Nettoyage optionnel des anciennes données pour cet ID
    cursor.execute("DELETE FROM iot_readings WHERE warehouse_id = ?", (WAREHOUSE_ID,))

    print(f"Génération de données pour {WAREHOUSE_ID}...")
    
    start_time = datetime.now() - timedelta(days=2)
    
    readings = []
    for i in range(100):
        recorded_at = (start_time + timedelta(minutes=30 * i)).strftime("%Y-%m-%d %H:%M:%S")
        
        # Simulation de température (autour de 22°C avec légère variation)
        t1 = round(22 + random.uniform(-2, 2), 2)
        t2 = round(22 + random.uniform(-2, 2), 2)
        t3 = round(22 + random.uniform(-2, 2), 2)
        
        # Simulation d'humidité (autour de 45% avec légère variation)
        h1 = round(45 + random.uniform(-5, 5), 2)
        h2 = round(45 + random.uniform(-5, 5), 2)
        h3 = round(45 + random.uniform(-5, 5), 2)
        
        readings.append((
            WAREHOUSE_ID, recorded_at, t1, t2, t3, h1, h2, h3
        ))

    cursor.executemany("""
        INSERT INTO iot_readings (
            warehouse_id, recorded_at, 
            temp_sensor_1, temp_sensor_2, temp_sensor_3, 
            hum_sensor_1, hum_sensor_2, hum_sensor_3
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, readings)

    conn.commit()
    conn.close()
    print(f"Succès : 100 points de données insérés pour {WAREHOUSE_ID}.")

if __name__ == "__main__":
    seed_iot_data()
