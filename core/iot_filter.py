import pandas as pd

from core.logistique import calculer_score_mixte, calculer_taux_conformite_iot, haversine
from utils.db import get_db_connection
from utils.product_conditions import (
    PRODUCT_CONDITIONS,
    get_product_storage_type,
    ignores_environment_conditions,
)


def get_compliant_warehouses(product_name, researcher_id=None):
    """
    Retourne les entrepots proprietaires conformes au produit choisi,
    puis les classe selon un score logistique calcule uniquement
    sur cet ensemble conforme.

    Etapes :
    1. Lire les entrepots de la base proprietaire (`warehouses`)
    2. Filtrer ceux qui sont conformes aux contraintes du produit
    3. Appliquer le calcul logistique sur les entrepots conformes
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

    delivery_center = None
    if researcher_id:
        df_points = pd.read_sql_query(
            """
            SELECT latitude, longitude
            FROM delivery_points
            WHERE researcher_id = ?
              AND latitude IS NOT NULL
              AND longitude IS NOT NULL
            """,
            conn,
            params=(researcher_id,),
        )
        if not df_points.empty:
            delivery_center = (
                float(df_points["latitude"].mean()),
                float(df_points["longitude"].mean()),
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

        df_temp_entrepot = df_iot.rename(
            columns={
                "temp_sensor_1": "capteur1",
                "temp_sensor_2": "capteur2",
                "temp_sensor_3": "capteur3",
            }
        )[["capteur1", "capteur2", "capteur3"]]

        df_humid_entrepot = df_iot.rename(
            columns={
                "hum_sensor_1": "capteur1",
                "hum_sensor_2": "capteur2",
                "hum_sensor_3": "capteur3",
            }
        )[["capteur1", "capteur2", "capteur3"]]

        if ignore_environment:
            iot_metrics = {
                "score_temp": 100.0,
                "score_hum": 100.0,
                "taux_conf": 100.0,
                "temp_moy": round(avg_temp, 2),
                "hum_moy": round(avg_hum, 2),
            }
        else:
            iot_metrics = calculer_taux_conformite_iot(
                df_temp_entrepot=df_temp_entrepot,
                df_humid_entrepot=df_humid_entrepot,
                type_stockage=type_stockage,
            )

        distance_km = None
        score_logistique = round((iot_metrics["score_temp"] + iot_metrics["score_hum"]) / 2, 2)

        if delivery_center is not None:
            distance_km = haversine(
                delivery_center[0],
                delivery_center[1],
                float(wh["latitude"]),
                float(wh["longitude"]),
            )
            score_logistique = calculer_score_mixte(
                distance=distance_km,
                score_temp=iot_metrics["score_temp"],
                score_hum=iot_metrics["score_hum"],
                poids={"dist": 0.5, "temp": 0.25, "hum": 0.25},
            )

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
                "taux_conf": float(iot_metrics["taux_conf"]),
                "score_temp": float(iot_metrics["score_temp"]),
                "score_hum": float(iot_metrics["score_hum"]),
                "distance_km": round(float(distance_km), 2) if distance_km is not None else None,
                "score_logistique": round(float(score_logistique), 2),
            }
        )

    conn.close()
    return sorted(compliant_list, key=lambda item: item["score_logistique"], reverse=True)
