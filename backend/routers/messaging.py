from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from schemas.messaging import ContactRequestResponse, ChatMessageResponse, ChatSendResponse
from dependencies.auth import get_current_user
from utils.db import load_sql_to_dataframe, execute_query
import sqlite3
from utils.db import DB_PATH

from core.messaging import (
    ensure_messaging_schema,
    get_owner_requests,
    update_contact_request_status,
    get_chat_messages,
    send_chat_message,
    create_contact_request,
)

router = APIRouter(prefix="/messaging", tags=["Messagerie"])


@router.get("/requests")
def get_requests(current_user: dict = Depends(get_current_user)):
    ensure_messaging_schema()
    uid = int(current_user["user_id"])
    role = current_user["role"]
    if role == "researcher":
        from core.messaging import get_researcher_requests
        df = get_researcher_requests(uid)
    elif role == "owner":
        df = get_owner_requests(uid)
    else:
        return []
    if df.empty:
        return []
    return df.to_dict(orient="records")


@router.post("/contact")
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


@router.post("/respond/{request_id}")
def respond_to_request(request_id: str, action: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "owner":
        raise HTTPException(status_code=403, detail="Réservé aux propriétaires")
    if action not in ("accepted", "rejected"):
        raise HTTPException(status_code=400, detail="Action must be 'accepted' or 'rejected'")
    ok = update_contact_request_status(request_id, int(current_user["user_id"]), action)
    if not ok:
        raise HTTPException(status_code=404, detail="Demande introuvable ou déjà traitée")
    return {"message": f"Demande {action}"}


@router.get("/chat/{request_id}")
def get_chat(request_id: str, _current_user: dict = Depends(get_current_user)):
    df = get_chat_messages(request_id)
    if df.empty:
        return []
    return df.to_dict(orient="records")


@router.post("/chat/{request_id}")
def send_chat(request_id: str, msg: str, current_user: dict = Depends(get_current_user)):
    ok, fb = send_chat_message(request_id, int(current_user["user_id"]), current_user["role"], msg)
    return {"ok": ok, "feedback": fb}


@router.post("/reservation/{request_id}/accept")
def accept_offer(request_id: str, current_user: dict = Depends(get_current_user)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE reservations SET status = 'confirmed' WHERE reservation_id = ?",
        (request_id,),
    )
    conn.commit()
    conn.close()
    return {"message": "Offre acceptée, accès IoT débloqué"}
