import sqlite3
import os

# Chemin vers la base de données
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database", "optistock.db"))

def migrate_iot_readings():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("Debut de la migration de la table iot_readings...")

        # 1. Verifier si la nouvelle table existe deja (au cas ou le script a crashé a la fin)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='iot_readings_new'")
        if cursor.fetchone():
            cursor.execute("DROP TABLE iot_readings_new")

        # 2. Créer une nouvelle table sans la contrainte de clé étrangère
        cursor.execute('''
            CREATE TABLE iot_readings_new (
                reading_id INTEGER PRIMARY KEY AUTOINCREMENT,
                warehouse_id TEXT NOT NULL,
                recorded_at DATETIME NOT NULL,
                temp_sensor_1 REAL,
                temp_sensor_2 REAL,
                temp_sensor_3 REAL,
                hum_sensor_1 REAL,
                hum_sensor_2 REAL,
                hum_sensor_3 REAL
            )
        ''')

        # 3. Copier les données de l'ancienne vers la nouvelle
        cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='iot_readings'")
        if cursor.fetchone()[0] > 0:
            cursor.execute('''
                INSERT INTO iot_readings_new 
                (reading_id, warehouse_id, recorded_at, temp_sensor_1, temp_sensor_2, temp_sensor_3, hum_sensor_1, hum_sensor_2, hum_sensor_3)
                SELECT reading_id, warehouse_id, recorded_at, temp_sensor_1, temp_sensor_2, temp_sensor_3, hum_sensor_1, hum_sensor_2, hum_sensor_3
                FROM iot_readings
            ''')
            cursor.execute("DROP TABLE iot_readings")

        # 4. Renommer
        cursor.execute("ALTER TABLE iot_readings_new RENAME TO iot_readings")

        conn.commit()
        print("SUCCESS: Migration terminee. La table est maintenant flexible.")

    except Exception as e:
        conn.rollback()
        print(f"FAILED: Erreur lors de la migration : {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_iot_readings()
