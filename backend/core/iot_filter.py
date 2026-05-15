import pandas as pd

from core.logistique import haversine
from utils.db import get_db_connection
from utils.product_conditions import (
    PRODUCT_CONDITIONS,
    get_product_storage_type,
    ignores_environment_conditions,
)


def get_compliant_warehouses(product_name, researcher_id=None):
    """
    Retourne les entrepots proprietaires conformes au produit choisi.
    Inclut les entrepôts 'available' ET 'maintenance'.
    Exclut uniquement les entrepôts 'rented' ou déjà dans la liste privée du chercheur.
    """
    conditions = PRODUCT_CONDITIONS.get(product_name)
    if not conditions:
        return []

    conn = get_db_connection()
    type_stockage = get_product_storage_type(product_name)
    ignore_environment = ignores_environment_conditions(product_name)

    # NOUVELLE REQUÊTE : On accepte 'available' et 'maintenance'
    query = """
        SELECT warehouse_id, owner_id, name, address, volume_m3, latitude, longitude, status, storage_type
        FROM warehouses
        WHERE latitude IS NOT NULL
          AND longitude IS NOT NULL
          AND (status = 'available' OR status = 'maintenance' OR status IS NULL OR status = '')
          AND status != 'rented'
    """
    params = []
    if researcher_id:
        query += " AND warehouse_id NOT IN (SELECT id_entrepot FROM my_warehouse WHERE researcher_id = ?)"
        params.append(researcher_id)

    df_warehouses = pd.read_sql_query(query, conn, params=params)

    compliant_list = []

    for _, wh in df_warehouses.iterrows():
        df_iot = pd.read_sql_query(
            """
            SELECT
                recorded_at,
                temp_sensor_1, temp_sensor_2, temp_sensor_3,
                hum_sensor_1, hum_sensor_2, hum_sensor_3
            FROM iot_readings
            WHERE warehouse_id = ?
            ORDER BY recorded_at
            """,
            conn,
            params=(wh["warehouse_id"],),
        )

        if df_iot.empty:
            avg_temp = 20.0 
            avg_hum = 50.0
            if ignore_environment:
                temp_ok = True
                hum_ok = True
            else:
                temp_ok = False
                hum_ok = False
        else:
            temp_series = df_iot[["temp_sensor_1", "temp_sensor_2", "temp_sensor_3"]].mean(axis=1)
            hum_series = df_iot[["hum_sensor_1", "hum_sensor_2", "hum_sensor_3"]].mean(axis=1)

            avg_temp = float(temp_series.mean())
            avg_hum = float(hum_series.mean())

            if ignore_environment:
                temp_ok = True
                hum_ok = True
            else:
                temp_min_allowed = conditions["temperature"]["min"] + conditions["temperature"]["marge_bas"]
                temp_max_allowed = conditions["temperature"]["max"] + conditions["temperature"]["marge_haut"]
                hum_min_allowed = conditions["humidite"]["min"] + conditions["humidite"]["marge_bas"]
                hum_max_allowed = conditions["humidite"]["max"] + conditions["humidite"]["marge_haut"]

                temp_ok = (
                    temp_min_allowed <= avg_temp <= temp_max_allowed and
                    temp_series.max() <= temp_max_allowed + 1.0 and
                    temp_series.min() >= temp_min_allowed - 1.0
                )
                hum_ok = (
                    hum_min_allowed <= avg_hum <= hum_max_allowed and
                    hum_series.max() <= hum_max_allowed + 5.0 and
                    hum_series.min() >= hum_min_allowed - 5.0
                )

        if type_stockage == "pharma" and wh["storage_type"] != "pharma":
            continue
        if type_stockage == "froid" and wh["storage_type"] not in ["froid", "pharma"]:
            continue

        if not (temp_ok and hum_ok):
            continue

        compliant_list.append(
            {
                "id": wh["warehouse_id"],
                "owner_id": wh["owner_id"],
                "nom": wh["name"],
                "adresse": wh["address"],
                "volume_m3": wh["volume_m3"],
                "avg_temp": round(avg_temp, 2),
                "avg_hum": round(avg_hum, 2),
                "latitude": wh["latitude"],
                "longitude": wh["longitude"],
                "status": wh["status"] or "available",
                "type_stockage": wh["storage_type"],
            }
        )

    conn.close()
    return compliant_list
