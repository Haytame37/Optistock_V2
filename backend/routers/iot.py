from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from typing import List

from schemas.iot import IoTReadingResponse, IoTKPI, IoTReading, IoTImportResponse
from dependencies.auth import get_current_user
from utils.db import load_sql_to_dataframe
from utils.product_conditions import PRODUCT_CONDITIONS
from core.iot_service import import_iot_csv
import pandas as pd
import numpy as np

router = APIRouter(prefix="/iot", tags=["IoT"])


@router.get("/readings/{warehouse_id}", response_model=IoTReadingResponse)
def get_readings(
    warehouse_id: str,
    product: str = "",
    index: int = -1,
    current_user: dict = Depends(get_current_user),
):
    from core.messaging import check_warehouse_access
    if not check_warehouse_access(warehouse_id, int(current_user["user_id"]), current_user["role"]):
        raise HTTPException(status_code=403, detail="Accès refusé. Vous devez avoir une réservation confirmée pour voir ces données.")

    query = f"""
        SELECT recorded_at, temp_sensor_1, temp_sensor_2, temp_sensor_3,
               hum_sensor_1, hum_sensor_2, hum_sensor_3
        FROM iot_readings WHERE warehouse_id = ?
        ORDER BY recorded_at
    """
    df = load_sql_to_dataframe(query, (warehouse_id,))
    if df.empty:
        raise HTTPException(status_code=404, detail="Aucune donnée IoT pour cet entrepôt")

    cols_t = ["temp_sensor_1", "temp_sensor_2", "temp_sensor_3"]
    cols_h = ["hum_sensor_1", "hum_sensor_2", "hum_sensor_3"]
    for col in cols_t + cols_h:
        df[col] = df[col].interpolate(method="linear", limit_direction="both")
        df[col] = df[col].rolling(window=3, min_periods=1).mean()

    df["T"] = df[cols_t].mean(axis=1)
    df["H"] = df[cols_h].mean(axis=1)

    idx = index if 0 <= index < len(df) else len(df) - 1
    current = df.iloc[idx]

    t_min = h_min = t_max = h_max = 0
    tol_t = tol_h = 999
    if product and product in PRODUCT_CONDITIONS:
        cond = PRODUCT_CONDITIONS[product]
        t_min, t_max = cond["temperature"]["min"], cond["temperature"]["max"]
        h_min, h_max = cond["humidite"]["min"], cond["humidite"]["max"]

    current_t = float(current["T"])
    current_h = float(current["H"])

    temp_status = "Optimal"
    temp_color = "#27ae60"
    if current_t < t_min:
        temp_status = "Alerte Basse"
        temp_color = "#f39c12"
    elif current_t > t_max:
        temp_status = "Alerte Haute"
        temp_color = "#f39c12"

    hum_status = "Optimal"
    hum_color = "#27ae60"
    if current_h < h_min:
        hum_status = "Alerte Basse"
        hum_color = "#f39c12"
    elif current_h > h_max:
        hum_status = "Alerte Haute"
        hum_color = "#f39c12"

    stability = 100
    if temp_status != "Optimal":
        stability -= 25
    if hum_status != "Optimal":
        stability -= 25

    readings = []
    for _, row in df.iterrows():
        readings.append(IoTReading(
            recorded_at=str(row["recorded_at"]),
            temp_sensor_1=float(row["temp_sensor_1"]) if pd.notna(row["temp_sensor_1"]) else None,
            temp_sensor_2=float(row["temp_sensor_2"]) if pd.notna(row["temp_sensor_2"]) else None,
            temp_sensor_3=float(row["temp_sensor_3"]) if pd.notna(row["temp_sensor_3"]) else None,
            hum_sensor_1=float(row["hum_sensor_1"]) if pd.notna(row["hum_sensor_1"]) else None,
            hum_sensor_2=float(row["hum_sensor_2"]) if pd.notna(row["hum_sensor_2"]) else None,
            hum_sensor_3=float(row["hum_sensor_3"]) if pd.notna(row["hum_sensor_3"]) else None,
        ))

    kpi = IoTKPI(
        current_temp=round(current_t, 1),
        current_hum=round(current_h, 1),
        avg_temp=round(float(df["T"].mean()), 1),
        avg_hum=round(float(df["H"].mean()), 1),
        temp_status=temp_status,
        hum_status=hum_status,
        temp_color=temp_color,
        hum_color=hum_color,
        stability_score=max(0, stability),
        consecutive_t_bad=0,
        consecutive_h_bad=0,
        tolerance_t=tol_t,
        tolerance_h=tol_h,
        trigger_alert=False,
    )

    return IoTReadingResponse(readings=readings, kpi=kpi, total=len(df), index=idx)


@router.post("/import/{warehouse_id}", response_model=IoTImportResponse)
def import_iot(warehouse_id: str, file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Seuls les fichiers CSV sont acceptés")
    try:
        df = pd.read_csv(file.file)
        success, message = import_iot_csv(warehouse_id, df)
        return IoTImportResponse(success=success, message=message, rows_imported=len(df) if success else 0)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur de lecture: {e}")


@router.get("/kpi/{warehouse_id}")
def get_kpi(warehouse_id: str, product: str = "", current_user: dict = Depends(get_current_user)):
    query = f"""
        SELECT recorded_at, temp_sensor_1, temp_sensor_2, temp_sensor_3,
               hum_sensor_1, hum_sensor_2, hum_sensor_3
        FROM iot_readings WHERE warehouse_id = '{warehouse_id}'
        ORDER BY recorded_at
    """
    df = load_sql_to_dataframe(query)
    if df.empty:
        raise HTTPException(status_code=404, detail="Aucune donnée IoT")
    cols_t = ["temp_sensor_1", "temp_sensor_2", "temp_sensor_3"]
    cols_h = ["hum_sensor_1", "hum_sensor_2", "hum_sensor_3"]
    for col in cols_t + cols_h:
        df[col] = df[col].interpolate(method="linear", limit_direction="both")
    df["T"] = df[cols_t].mean(axis=1)
    df["H"] = df[cols_h].mean(axis=1)

    return {
        "avg_temp": round(float(df["T"].mean()), 1),
        "avg_hum": round(float(df["H"].mean()), 1),
        "min_temp": round(float(df["T"].min()), 1),
        "max_temp": round(float(df["T"].max()), 1),
        "min_hum": round(float(df["H"].min()), 1),
        "max_hum": round(float(df["H"].max()), 1),
        "count": len(df),
    }
