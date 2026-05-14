import pandas as pd
import numpy as np
from utils.db import get_db_connection

def clean_iot_dataframe(df):
    """
    Applique les règles de nettoyage du script clean_data.py :
    - Interpolation des valeurs manquantes.
    - Suppression des aberrations (Outliers).
    """
    # 1. Interpolation linéaire pour boucher les trous (NaN)
    # On ne le fait que sur les colonnes numériques de capteurs
    sensor_cols = [c for c in df.columns if 'temp_sensor' in c or 'hum_sensor' in c]
    df[sensor_cols] = df[sensor_cols].interpolate(method='linear', limit_direction='both')
    
    # 2. Suppression des aberrations (Filtrage)
    # Températures : entre -20°C et 60°C
    for col in [c for c in df.columns if 'temp_sensor' in c]:
        df.loc[(df[col] < -20) | (df[col] > 60), col] = np.nan
        
    # Humidité : entre 0% et 100%
    for col in [c for c in df.columns if 'hum_sensor' in c]:
        df.loc[(df[col] < 0) | (df[col] > 100), col] = np.nan
        
    # On ré-interpole après avoir supprimé les aberrations pour lisser la courbe
    df[sensor_cols] = df[sensor_cols].interpolate(method='linear', limit_direction='both')
    
    return df

def import_iot_csv(warehouse_id, df):
    """
    Importe et NETTOIE les données environnementales d'un DataFrame CSV.
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

    # --- ÉTAPE DE NETTOYAGE (Fusion de clean_data.py) ---
    df = clean_iot_dataframe(df)
    # ----------------------------------------------------

    # Conversion finale des dates
    df['recorded_at'] = pd.to_datetime(df['recorded_at'], errors='coerce')
    df = df.dropna(subset=['recorded_at'])
    df['recorded_at'] = df['recorded_at'].dt.strftime('%Y-%m-%d %H:%M:%S')

    rows = df[['recorded_at'] + sensor_cols].values.tolist()

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM iot_readings WHERE warehouse_id = ?", (warehouse_id,))
        cursor.executemany("""
            INSERT INTO iot_readings 
                (warehouse_id, recorded_at, temp_sensor_1, temp_sensor_2, temp_sensor_3,
                 hum_sensor_1, hum_sensor_2, hum_sensor_3)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [(warehouse_id, *r) for r in rows])
        conn.commit()
        return True, f"✅ {len(rows)} lectures IoT nettoyées et importées avec succès."
    except Exception as e:
        print(f"Error importing IoT CSV: {e}")
        return False, f"❌ Erreur lors de l'import : {e}"
    finally:
        if conn:
            conn.close()
