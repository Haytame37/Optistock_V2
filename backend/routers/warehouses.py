from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import APIRouter, Depends, HTTPException, status
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

router = APIRouter(prefix="/warehouses", tags=["Entrepôts"])


@router.get("/my")
def my_warehouses(current_user: dict = Depends(get_current_user)):
    uid = int(current_user["user_id"])
    role = current_user["role"]
    if role == "owner":
        items = get_warehouses_by_owner(uid)
        return items
    elif role == "researcher":
        df = load_sql_to_dataframe(
            "SELECT id_entrepot, nom, adresse, latitude, longitude FROM my_warehouse WHERE researcher_id = ?",
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
    wid = add_warehouse(
        owner_id=int(current_user["user_id"]),
        name=wh.name,
        address=wh.address,
        volume_m3=wh.volume_m3,
        latitude=wh.latitude,
        longitude=wh.longitude,
    )
    if wid is None:
        raise HTTPException(status_code=500, detail="Erreur lors de la création")
    return {"warehouse_id": wid, "message": "Entrepôt créé"}


@router.get("/{warehouse_id}")
def get_warehouse(warehouse_id: str):
    row = get_warehouse_by_id(warehouse_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Entrepôt introuvable")
    return {
        "warehouse_id": warehouse_id,
        "name": row["name"],
        "address": row["address"],
        "volume_m3": row["volume_m3"],
        "latitude": row["latitude"],
        "longitude": row["longitude"],
    }


@router.put("/{warehouse_id}")
def update_warehouse_endpoint(warehouse_id: str, wh: WarehouseUpdate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "owner":
        raise HTTPException(status_code=403, detail="Réservé aux propriétaires")
    ok = update_warehouse(warehouse_id, wh.name, wh.address, wh.volume_m3, wh.latitude, wh.longitude)
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
