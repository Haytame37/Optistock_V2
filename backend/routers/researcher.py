from __future__ import annotations

import sys, os, json, uuid
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
from scipy.optimize import minimize
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from schemas.researcher import (
    SearchRequest,
    SearchResponse,
    SearchResultItem,
    WeberResponse,
    SearchHistoryItem,
    ClientPoint,
    MyWarehouse,
)
from schemas.messaging import ContactRequestResponse, ChatMessageResponse, ChatSendResponse
from dependencies.auth import get_current_user
from utils.db import DB_PATH, load_sql_to_dataframe, execute_query
import sqlite3

from core.iot_filter import get_compliant_warehouses
from core.logistique import classer_entrepots_logistique, haversine
from core.messaging import (
    create_contact_request,
    get_researcher_requests,
    get_chat_messages,
    send_chat_message,
    ensure_messaging_schema,
)

router = APIRouter(prefix="/researcher", tags=["Chercheur"])


def fermat_weber(points: np.ndarray) -> tuple:
    def objective(p):
        diffs = points - p
        return np.sum(np.sqrt((diffs ** 2).sum(axis=1)))
    x0 = points.mean(axis=0)
    result = minimize(objective, x0, method="L-BFGS-B")
    lat_opt, lon_opt = result.x
    R = 6371.0
    lat1_r = np.radians(points[:, 0])
    lon1_r = np.radians(points[:, 1])
    lat2_r = np.radians(lat_opt)
    lon2_r = np.radians(lon_opt)
    dlat = lat2_r - lat1_r
    dlon = lon2_r - lon1_r
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1_r) * np.cos(lat2_r) * np.sin(dlon / 2) ** 2
    avg_dist_km = float(np.mean(2 * R * np.arctan2(np.sqrt(a), np.sqrt(1 - a))))
    return float(lat_opt), float(lon_opt), avg_dist_km


@router.post("/search", response_model=SearchResponse)
def search_warehouses(req: SearchRequest, current_user: dict = Depends(get_current_user)):
    researcher_id = int(current_user["user_id"])
    compliant = get_compliant_warehouses(req.product)
    suggestions = classer_entrepots_logistique(compliant, researcher_id)
    saved_points = 0
    saved_warehouses = 0

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if req.clients:
        cursor.execute("DELETE FROM delivery_points WHERE researcher_id = ?", (researcher_id,))
        for c in req.clients:
            cursor.execute(
                "INSERT INTO delivery_points (request_id, researcher_id, name, latitude, longitude) VALUES (?, ?, ?, ?, ?)",
                (str(uuid.uuid4())[:8], researcher_id, c.name, c.latitude, c.longitude),
            )
        saved_points = len(req.clients)
    if req.warehouses:
        cursor.execute("DELETE FROM my_warehouse WHERE researcher_id = ?", (researcher_id,))
        for w in req.warehouses:
            cursor.execute(
                "INSERT OR REPLACE INTO my_warehouse (id_entrepot, researcher_id, nom, adresse, latitude, longitude) VALUES (?, ?, ?, ?, ?, ?)",
                (w.id_entrepot, researcher_id, w.nom, w.adresse, w.latitude, w.longitude),
            )
        saved_warehouses = len(req.warehouses)
    conn.commit()
    conn.close()

    results_json = json.dumps(suggestions, default=str)
    execute_query(
        "INSERT INTO search_history (researcher_id, product_name, volume, duration_days, results_json) VALUES (?, ?, ?, ?, ?)",
        (researcher_id, req.product, req.volume, req.duration_days, results_json),
    )

    items = [SearchResultItem(**s) for s in suggestions]
    return SearchResponse(
        results=items,
        product=req.product,
        volume=req.volume,
        duration_days=req.duration_days,
        saved_points=saved_points,
        saved_warehouses=saved_warehouses,
    )


@router.post("/weber", response_model=WeberResponse)
def weber_calculation(clients: List[ClientPoint], _current_user: dict = Depends(get_current_user)):
    if len(clients) < 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Au moins 2 clients requis")
    pts = np.array([[c.latitude, c.longitude] for c in clients])
    lat_opt, lon_opt, avg_dist = fermat_weber(pts)
    return WeberResponse(lat_opt=lat_opt, lon_opt=lon_opt, avg_distance_km=avg_dist)


@router.get("/history", response_model=List[SearchHistoryItem])
def search_history(current_user: dict = Depends(get_current_user)):
    df = load_sql_to_dataframe(
        "SELECT id, product_name, volume, duration_days, results_json, created_at FROM search_history WHERE researcher_id = ? ORDER BY created_at DESC",
        (int(current_user["user_id"]),),
    )
    return [SearchHistoryItem(**row) for _, row in df.iterrows()]


@router.get("/history/{history_id}", response_model=SearchResponse)
def get_history_detail(history_id: int, current_user: dict = Depends(get_current_user)):
    df = load_sql_to_dataframe(
        "SELECT product_name, volume, duration_days, results_json FROM search_history WHERE id = ? AND researcher_id = ?",
        (history_id, int(current_user["user_id"])),
    )
    if df.empty:
        raise HTTPException(status_code=404, detail="Historique introuvable")
    row = df.iloc[0]
    results = json.loads(row["results_json"])
    items = [SearchResultItem(**s) for s in results]
    return SearchResponse(
        results=items,
        product=row["product_name"],
        volume=row["volume"],
        duration_days=row["duration_days"],
    )


@router.post("/contact", response_model=dict)
def contact_owner(
    warehouse_id: str,
    owner_id: int,
    product_name: str,
    message: str,
    current_user: dict = Depends(get_current_user),
):
    ensure_messaging_schema()
    ok, payload = create_contact_request(
        warehouse_id=warehouse_id,
        owner_id=owner_id,
        researcher_id=int(current_user["user_id"]),
        product_name=product_name,
        message=message,
    )
    return {"ok": ok, "payload": payload}


@router.get("/messages", response_model=List[ContactRequestResponse])
def get_messages(current_user: dict = Depends(get_current_user)):
    df = get_researcher_requests(int(current_user["user_id"]))
    if df.empty:
        return []
    return [ContactRequestResponse(**row) for _, row in df.iterrows()]


@router.get("/chat/{request_id}", response_model=List[ChatMessageResponse])
def get_chat(request_id: str, _current_user: dict = Depends(get_current_user)):
    df = get_chat_messages(request_id)
    if df.empty:
        return []
    return [ChatMessageResponse(**row) for _, row in df.iterrows()]


@router.post("/chat/{request_id}", response_model=ChatSendResponse)
def send_chat(request_id: str, msg: str, current_user: dict = Depends(get_current_user)):
    ok, fb = send_chat_message(request_id, int(current_user["user_id"]), current_user["role"], msg)
    return ChatSendResponse(ok=ok, feedback=fb)
