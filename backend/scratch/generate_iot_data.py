import sqlite3
import random
import datetime
import os

db_path = os.path.join('database', 'optistock.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

warehouse_id = 'ENT001'
now = datetime.datetime.now()

# Supprimer les anciennes données pour être sûr
cursor.execute("DELETE FROM iot_readings WHERE warehouse_id = ?", (warehouse_id,))

# Générer 100 points de données (15 minutes d'intervalle)
for i in range(100):
    recorded_at = (now - datetime.timedelta(minutes=15 * (100 - i))).strftime('%Y-%m-%d %H:%M:%S')
    
    # Simuler des données de réfrigération (entre 2 et 8 degrés)
    t1 = random.uniform(3.5, 5.5)
    t2 = random.uniform(3.2, 5.8)
    t3 = random.uniform(3.8, 6.2)
    
    # Simuler une humidité stable (entre 88 et 92%)
    h1 = random.uniform(89.5, 91.5)
    h2 = random.uniform(88.0, 92.0)
    h3 = random.uniform(90.0, 91.0)
    
    cursor.execute('''
        INSERT INTO iot_readings 
        (warehouse_id, recorded_at, temp_sensor_1, temp_sensor_2, temp_sensor_3, hum_sensor_1, hum_sensor_2, hum_sensor_3) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (warehouse_id, recorded_at, t1, t2, t3, h1, h2, h3))

conn.commit()
conn.close()
print(f"100 relevés IoT générés avec succès pour l'entrepôt {warehouse_id} !")
