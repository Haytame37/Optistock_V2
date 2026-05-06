import pandas as pd
from utils.db import get_db_connection

def import_iot_csv(warehouse_id, df):
    """
    Importe les données environnementales d'un DataFrame CSV dans iot_readings.
    Le CSV doit contenir une colonne de date/heure et au moins une colonne
    de température ou d'humidité.
    """
    # Normalisation des noms de colonnes
    df.columns = [c.strip().lower() for c in df.columns]
    
    MAPPING = {
        'recorded_at':  ['date', 'datetime', 'heure', 'timestamp', 'time', 'recorded_at'],
        'temp_sensor_1': ['temp_1', 'temperature_1', 't1', 'temp1', 'temperature1'],
        'temp_sensor_2': ['temp_2', 'temperature_2', 't2', 'temp2', 'temperature2'],
        'temp_sensor_3': ['temp_3', 'temperature_3', 't3', 'temp3', 'temperature3'],
        'hum_sensor_1':  ['hum_1', 'humidite_1', 'humidity_1', 'h1', 'hum1'],
        'hum_sensor_2':  ['hum_2', 'humidite_2', 'humidity_2', 'h2', 'hum2'],
        'hum_sensor_3':  ['hum_3', 'humidite_3', 'humidity_3', 'h3', 'hum3'],
    }

    renamed = {}
    for target_col, aliases in MAPPING.items():
        for alias in aliases:
            if alias in df.columns and target_col not in renamed:
                renamed[alias] = target_col
                break

    df = df.rename(columns=renamed)

    if 'recorded_at' not in df.columns:
        return False, "❌ Colonne date/heure introuvable. Vérifiez que votre CSV contient une colonne 'date', 'datetime' ou 'timestamp'."

    sensor_cols = ['temp_sensor_1', 'temp_sensor_2', 'temp_sensor_3',
                   'hum_sensor_1',  'hum_sensor_2',  'hum_sensor_3']

    # Ajouter les colonnes manquantes avec None
    for col in sensor_cols:
        if col not in df.columns:
            df[col] = None

    # Nettoyage
    df['recorded_at'] = pd.to_datetime(df['recorded_at'], errors='coerce')
    df = df.dropna(subset=['recorded_at'])
    df['recorded_at'] = df['recorded_at'].dt.strftime('%Y-%m-%d %H:%M:%S')

    rows = df[['recorded_at'] + sensor_cols].values.tolist()

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Supprimer les anciennes données pour éviter les doublons
        cursor.execute("DELETE FROM iot_readings WHERE warehouse_id = ?", (warehouse_id,))
        cursor.executemany("""
            INSERT INTO iot_readings 
                (warehouse_id, recorded_at, temp_sensor_1, temp_sensor_2, temp_sensor_3,
                 hum_sensor_1, hum_sensor_2, hum_sensor_3)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [(warehouse_id, *r) for r in rows])
        conn.commit()
        return True, f"✅ {len(rows)} lectures IoT importées avec succès."
    except Exception as e:
        print(f"Error importing IoT CSV: {e}")
        return False, f"❌ Erreur lors de l'import : {e}"
    finally:
        if conn:
            conn.close()
