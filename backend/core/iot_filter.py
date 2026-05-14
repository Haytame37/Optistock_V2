import pandas as pd

from core.logistique import haversine
from utils.db import get_db_connection
from utils.product_conditions import (
    PRODUCT_CONDITIONS,
    get_product_storage_type,
    ignores_environment_conditions,
)


def get_compliant_warehouses(product_name):
    """
    Retourne les entrepots proprietaires conformes au produit choisi,
    sans aucun calcul logistique.

    Etapes :
    1. Lire les entrepots de la base proprietaire (`warehouses`)
    2. Filtrer ceux qui sont conformes aux contraintes du produit
    """
    conditions = PRODUCT_CONDITIONS.get(product_name)
    if not conditions:
        return []

    conn = get_db_connection()
    type_stockage = get_product_storage_type(product_name)
    ignore_environment = ignores_environment_conditions(product_name)

    df_warehouses = pd.read_sql_query(
        """
        SELECT warehouse_id, owner_id, name, address, volume_m3, latitude, longitude, status
        FROM warehouses
        WHERE latitude IS NOT NULL
          AND longitude IS NOT NULL
        """,
        conn,
    )



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
            continue

        temp_series = df_iot[["temp_sensor_1", "temp_sensor_2", "temp_sensor_3"]].mean(axis=1)
        hum_series = df_iot[["hum_sensor_1", "hum_sensor_2", "hum_sensor_3"]].mean(axis=1)

        avg_temp = float(temp_series.mean())
        avg_hum = float(hum_series.mean())

        if ignore_environment:
            temp_ok = True
            hum_ok = True
        else:
            temp_ok = (
                conditions["temperature"]["min"] + conditions["temperature"]["marge_bas"]
                <= avg_temp
                <= conditions["temperature"]["max"] + conditions["temperature"]["marge_haut"]
            )
            hum_ok = (
                conditions["humidite"]["min"] + conditions["humidite"]["marge_bas"]
                <= avg_hum
                <= conditions["humidite"]["max"] + conditions["humidite"]["marge_haut"]
            )

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
                "status": wh["status"],
                "type_stockage": type_stockage,
            }
        )

    conn.close()
    return compliant_list
