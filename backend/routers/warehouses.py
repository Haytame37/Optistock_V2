from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List

from schemas.warehouse import WarehouseCreate, WarehouseUpdate, WarehouseResponse, WarehouseListItem
from schemas.researcher import ClientPoint, MyWarehouse
from dependencies.auth import get_current_user
from utils.db import DB_PATH, load_sql_to_dataframe, execute_query
import sqlite3

from core.warehouse_service import (
    add_warehouse,
    delete_warehouse,
    get_warehouse_by_id,
    update_warehouse,
    get_warehouses_by_owner,
    get_recent_warehouses_by_owner,
)

from pydantic import BaseModel
from utils.email_utils import send_iot_alert_email

router = APIRouter(prefix="/warehouses", tags=["Entrepôts"])

class AlertRequest(BaseModel):
    email: str
    warehouse_name: str
    product_name: str
    temp: float
    hum: float

@router.post("/alert")
async def trigger_iot_alert(req: AlertRequest, background_tasks: BackgroundTasks):
    # On lance l'envoi en arrière-plan pour ne pas bloquer le dashboard
    background_tasks.add_task(
        send_iot_alert_email, 
        req.email, 
        req.warehouse_name, 
        req.product_name, 
        req.temp, 
        req.hum
    )
    return {"status": "processing"}


@router.get("/my")
def my_warehouses(current_user: dict = Depends(get_current_user)):
    uid = int(current_user["user_id"])
    role = current_user["role"]
    if role == "owner":
        items = get_warehouses_by_owner(uid)
        return items
    elif role == "researcher":
        df = load_sql_to_dataframe(
            "SELECT id_entrepot, nom, adresse, latitude, longitude, product_name FROM my_warehouse WHERE researcher_id = ?",
            (uid,),
        )
        if df.empty:
            return []
        return df.to_dict(orient="records")
    return []


@router.get("/owner")
def owner_warehouses(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "owner":
        raise HTTPException(status_code=403, detail="Réservé aux propriétaires")
    items = get_warehouses_by_owner(int(current_user["user_id"]))
    return items


@router.get("/owner/recent")
def recent_warehouses(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "owner":
        raise HTTPException(status_code=403, detail="Réservé aux propriétaires")
    return get_recent_warehouses_by_owner(int(current_user["user_id"]))


@router.post("")
def create_warehouse(wh: WarehouseCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "owner":
        raise HTTPException(status_code=403, detail="Réservé aux propriétaires")
    try:
        wid = add_warehouse(
            owner_id=int(current_user["user_id"]),
            name=wh.name,
            address=wh.address,
            volume_m3=wh.volume_m3,
            latitude=wh.latitude,
            longitude=wh.longitude,
            iot_token=wh.iot_token
        )
        return {"warehouse_id": wid, "message": "Entrepôt créé"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{warehouse_id}")
def get_warehouse(warehouse_id: str, current_user: dict = Depends(get_current_user)):
    uid = int(current_user["user_id"])
    row = get_warehouse_by_id(warehouse_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Entrepôt introuvable")
    
    # Chercher si un produit est associé pour ce chercheur
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT product_name FROM my_warehouse WHERE id_entrepot = ? AND researcher_id = ?", (warehouse_id, uid))
    asset = cursor.fetchone()
    product_name = asset["product_name"] if asset else None
    conn.close()

    return {
        "warehouse_id": warehouse_id,
        "name": row["name"],
        "address": row["address"],
        "volume_m3": row["volume_m3"],
        "latitude": row["latitude"],
        "longitude": row["longitude"],
        "iot_token": row["iot_token"],
        "product_name": product_name
    }


@router.put("/{warehouse_id}")
def update_warehouse_endpoint(warehouse_id: str, wh: WarehouseUpdate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "owner":
        raise HTTPException(status_code=403, detail="Réservé aux propriétaires")
    ok = update_warehouse(warehouse_id, wh.name, wh.address, wh.volume_m3, wh.latitude, wh.longitude, wh.status, wh.iot_token)
    if not ok:
        raise HTTPException(status_code=404, detail="Entrepôt introuvable")
    return {"message": "Entrepôt mis à jour"}


@router.delete("/{warehouse_id}")
def delete_warehouse_endpoint(warehouse_id: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "owner":
        raise HTTPException(status_code=403, detail="Réservé aux propriétaires")
    ok = delete_warehouse(warehouse_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Entrepôt introuvable")
    return {"message": "Entrepôt supprimé"}

@router.patch("/{warehouse_id}/status")
def update_warehouse_status(
    warehouse_id: str, 
    status: str, 
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "owner":
        raise HTTPException(status_code=403, detail="Réservé aux propriétaires")
    
    valid_statuses = ["available", "maintenance", "rented"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Statut invalide. Choisissez parmi : {valid_statuses}")

    # 1. On vérifie d'abord que l'entrepôt appartient bien au propriétaire
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT owner_id FROM warehouses WHERE warehouse_id = ?", (warehouse_id,))
    row = cursor.fetchone()
    if not row or row[0] != int(current_user["user_id"]):
        conn.close()
        raise HTTPException(status_code=403, detail="Permission refusée ou entrepôt introuvable")

    # 2. Mise à jour du statut
    cursor.execute("UPDATE warehouses SET status = ? WHERE warehouse_id = ?", (status, warehouse_id))
    conn.commit()
    conn.close()

    # 3. Libération totale si demandé 'available'
    if status == "available":
        print(f">>> LIBÉRATION TOTALE FORCÉE : {warehouse_id}")
        execute_query("DELETE FROM my_warehouse WHERE id_entrepot = ?", (warehouse_id,))
        execute_query("DELETE FROM reservations WHERE warehouse_id = ?", (warehouse_id,))
        execute_query("DELETE FROM contact_requests WHERE warehouse_id = ?", (warehouse_id,))
        
    return {"message": f"Statut mis à jour : {status}"}
