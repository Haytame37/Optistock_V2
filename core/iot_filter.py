import pandas as pd
import sqlite3
from utils.db import get_db_connection, DB_PATH
from utils.product_conditions import PRODUCT_CONDITIONS

def get_compliant_warehouses(product_name, researcher_id=None):
    """
    Retourne une liste d'entrepôts conformes aux conditions du produit.
    Si researcher_id est fourni, on priorise les entrepôts importés par ce chercheur.
    Sinon, on cherche dans le catalogue global.
    """
    conditions = PRODUCT_CONDITIONS.get(product_name)
    if not conditions:
        return []

    conn = get_db_connection()
    
    # 1. Récupération des entrepôts à analyser
    # On unifie les sources : warehouses (owner_id) et my_warehouse (researcher_id)
    # On utilise des alias pour lever la contradiction d'ID d'owner
    
    if researcher_id:
        # Priorité aux entrepôts du chercheur (ses "élements fournis")
        query_wh = """
            SELECT id_entrepot as warehouse_id, researcher_id as owner_id, nom as name, latitude, longitude, 'available' as status
            FROM my_warehouse
            WHERE researcher_id = ?
        """
        df_warehouses = pd.read_sql_query(query_wh, conn, params=(researcher_id,))
        
        # Si le chercheur n'a rien importé, on peut éventuellement proposer le catalogue global
        if df_warehouses.empty:
            query_global = """
                SELECT warehouse_id, owner_id, name, latitude, longitude, status
                FROM warehouses
            """
            df_warehouses = pd.read_sql_query(query_global, conn)
    else:
        # Recherche globale par défaut
        query_global = """
            SELECT warehouse_id, owner_id, name, latitude, longitude, status
            FROM warehouses
        """
        df_warehouses = pd.read_sql_query(query_global, conn)
    
    compliant_list = []
    
    for _, wh in df_warehouses.iterrows():
        wh_id = wh['warehouse_id']
        
        # Récupérer les moyennes IoT de l'historique existant dans la base
        query_iot = """
            SELECT 
                AVG((temp_sensor_1 + temp_sensor_2 + temp_sensor_3) / 3.0) as avg_temp,
                AVG((hum_sensor_1 + hum_sensor_2 + hum_sensor_3) / 3.0) as avg_hum
            FROM iot_readings
            WHERE warehouse_id = ?
        """
        df_stats = pd.read_sql_query(query_iot, conn, params=(wh_id,))
        
        if df_stats.empty or df_stats['avg_temp'].iloc[0] is None:
            # Si pas de données IoT, l'entrepôt ne peut pas être validé "par historique"
            continue
            
        avg_temp = df_stats['avg_temp'].iloc[0]
        avg_hum = df_stats['avg_hum'].iloc[0]
        
        # Vérification de la conformité (Ideal + Marges)
        temp_ok = (conditions['temperature']['min'] + conditions['temperature']['marge_bas'] <= avg_temp <= 
                   conditions['temperature']['max'] + conditions['temperature']['marge_haut'])
        hum_ok = (conditions['humidite']['min'] + conditions['humidite']['marge_bas'] <= avg_hum <= 
                  conditions['humidite']['max'] + conditions['humidite']['marge_haut'])
        
        if temp_ok and hum_ok:
            compliant_list.append({
                "id": wh_id,
                "owner_id": wh['owner_id'], # ID unifié (chercheur ou propriétaire)
                "nom": wh['name'],
                "avg_temp": round(avg_temp, 2),
                "avg_hum": round(avg_hum, 2),
                "latitude": wh['latitude'],
                "longitude": wh['longitude'],
                "status": wh['status']
            })
            
    conn.close()
    return compliant_list