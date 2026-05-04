import pandas as pd
import sqlite3
import os
import glob
import sys

# Allow importing from parent package
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.helpers import get_current_time

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "optistock.db"))
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "samples")

def seed_database():
    """Charge les données CSV générées et les fusionne dans le nouveau schéma EARSER."""
    print("Demarrage de l'importation vers SQLite (Schema EARSER)...")
    
    if not os.path.exists(DB_PATH):
        print("La base optistock.db n'existe pas. Executez init_db.py d'abord.")
        return
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Création d'utilisateurs par défaut pour satisfaire les contraintes de clés étrangères
    print("Creation des 5 utilisateurs par defaut (1 admin, 2 owners, 2 researchers)...")
    
    import hashlib
    def hash_pw(pwd):
        return hashlib.sha256(pwd.encode()).hexdigest()
        
    hashed_pw = hash_pw("password123")
    
    now_str = get_current_time().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute(f"""
        INSERT OR IGNORE INTO users (user_id, role, first_name, last_name, email, password_hash, created_at, updated_at)
        VALUES 
            (1, 'admin', 'Admin', 'Principal', 'admin@optistock.com', '{hashed_pw}', '{now_str}', '{now_str}'),
            (2, 'owner', 'Propriétaire', 'Un', 'owner1@optistock.com', '{hashed_pw}', '{now_str}', '{now_str}'),
            (3, 'owner', 'Propriétaire', 'Deux', 'owner2@optistock.com', '{hashed_pw}', '{now_str}', '{now_str}'),
            (4, 'researcher', 'Chercheur', 'Alpha', 'researcher1@optistock.com', '{hashed_pw}', '{now_str}', '{now_str}'),
            (5, 'researcher', 'Chercheur', 'Beta', 'researcher2@optistock.com', '{hashed_pw}', '{now_str}', '{now_str}')
    """)
    
    # 2. Importation du Catalogue Entrepôts (entrepots.csv -> warehouses)
    entrepots_csv = os.path.join(DATA_DIR, "entrepots.csv")
    if os.path.exists(entrepots_csv):
        df_entrepots = pd.read_csv(entrepots_csv)
        print(f"Importation de {len(df_entrepots)} entrepots dans la table 'warehouses'...")
        
        # Adaptation au nouveau format 'warehouses'
        # Colonnes attendues: warehouse_id, owner_id, name, volume_m3, latitude, longitude, status
        df_wh = pd.DataFrame()
        df_wh["warehouse_id"] = df_entrepots["id_entrepot"]
        # Assigner de manière aléatoire aux owner 2 et 3
        df_wh["owner_id"] = [2 if i % 2 == 0 else 3 for i in range(len(df_entrepots))]
        df_wh["name"] = "Entrepôt " + df_entrepots["id_entrepot"]
        df_wh["volume_m3"] = 10000.0  # Valeur par défaut
        df_wh["latitude"] = df_entrepots["latitude"]
        df_wh["longitude"] = df_entrepots["longitude"]
        df_wh["status"] = "available"
        
        df_wh.to_sql("warehouses", conn, if_exists="append", index=False)
    else:
        print("Fichier entrepots.csv introuvable.")

    # 3. Fusion et importation des données IoT (temperature_*.csv + humidite_*.csv -> iot_readings)
    temp_files = sorted(glob.glob(os.path.join(DATA_DIR, "temperature_ENT*.csv")))
    
    if temp_files:
        print(f"Fusion et importation de {len(temp_files)} fichiers IoT (Temp + Hum) -> iot_readings...")
        total_rows = 0
        for f_temp in temp_files:
            # Extraire l'ID de l'entrepôt depuis le nom du fichier (ex: temperature_ENT001.csv)
            basename = os.path.basename(f_temp)
            wh_id = basename.replace("temperature_", "").replace(".csv", "")
            
            f_hum = os.path.join(DATA_DIR, f"humidite_{wh_id}.csv")
            
            if not os.path.exists(f_hum):
                print(f"Fichier d'humidite correspondant introuvable pour {wh_id}. Ignore.")
                continue

            df_t = pd.read_csv(f_temp)
            df_h = pd.read_csv(f_hum)
            
            # Fusion sur datetime
            df_merged = pd.merge(
                df_t[["datetime", "capteur1", "capteur2", "capteur3"]],
                df_h[["datetime", "capteur1", "capteur2", "capteur3"]],
                on="datetime",
                how="inner",
                suffixes=("_t", "_h")
            )
            
            # Préparation du format iot_readings
            df_iot = pd.DataFrame({
                "recorded_at": df_merged["datetime"]
            })
            df_iot["warehouse_id"] = wh_id
            df_iot["temp_sensor_1"] = df_merged["capteur1_t"]
            df_iot["temp_sensor_2"] = df_merged["capteur2_t"]
            df_iot["temp_sensor_3"] = df_merged["capteur3_t"]
            df_iot["hum_sensor_1"] = df_merged["capteur1_h"]
            df_iot["hum_sensor_2"] = df_merged["capteur2_h"]
            df_iot["hum_sensor_3"] = df_merged["capteur3_h"]
            
            df_iot.to_sql("iot_readings", conn, if_exists="append", index=False)
            total_rows += len(df_iot)
            
        print(f"{total_rows} enregistrements IoT fusionnes et importes.")
    else:
        print("Aucun fichier de capteurs trouve.")
        
    conn.commit()
    conn.close()
    print("Base de donnees SQLite (EARSER) peuplee avec succes !")

if __name__ == "__main__":
    seed_database()
