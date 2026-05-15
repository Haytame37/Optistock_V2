from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
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


from utils.email_utils import send_offer_received_email, send_acceptance_confirmation_email

@router.post("/offer/{request_id}")
def send_offer(
    request_id: str, 
    price: float, 
    start_date: str, 
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "owner":
        raise HTTPException(status_code=403, detail="Réservé aux propriétaires")
    
    from core.messaging import create_rental_offer
    ok, fb = create_rental_offer(request_id, int(current_user["user_id"]), price, start_date)
    
    if ok:
        # NOTIFICATION EMAIL AU CHERCHEUR (EN ARRIÈRE-PLAN)
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT u.email, w.name as warehouse_name, 
                       (SELECT full_name FROM users WHERE user_id = ?) as owner_name
                FROM contact_requests cr 
                JOIN users u ON cr.researcher_id = u.user_id 
                JOIN warehouses w ON cr.warehouse_id = w.warehouse_id 
                WHERE cr.request_id = ?
                """,
                (int(current_user["user_id"]), request_id)
            )
            row = cursor.fetchone()
            if row:
                background_tasks.add_task(
                    send_offer_received_email, 
                    row["email"], 
                    row["owner_name"] or "Un Propriétaire", 
                    row["warehouse_name"]
                )
            conn.close()
        except Exception as e:
            print(f"Erreur préparation email offre : {e}")

    return {"ok": ok, "feedback": fb}


@router.post("/reservation/{request_id}/accept")
def accept_offer(
    request_id: str, 
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    uid = int(current_user["user_id"])
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # 1. Trouver la réservation
        cursor.execute(
            "SELECT warehouse_id, status, (SELECT product_name FROM contact_requests WHERE request_id = reservations.reservation_id OR warehouse_id = reservations.warehouse_id LIMIT 1) as product_name FROM reservations WHERE (reservation_id = ? OR warehouse_id = ?) AND researcher_id = ?",
            (request_id, request_id, uid)
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Aucune offre trouvée pour cet identifiant.")
        
        warehouse_id = row["warehouse_id"]
        product_name = row["product_name"]
        is_already_confirmed = row["status"] == "confirmed"

        # 2. Confirmer la réservation
        if not is_already_confirmed:
            cursor.execute(
                "UPDATE reservations SET status = 'confirmed' WHERE (reservation_id = ? OR warehouse_id = ?) AND researcher_id = ?",
                (request_id, request_id, uid)
            )

        # 3. Récupérer les détails de l'entrepôt
        cursor.execute(
            "SELECT name, address, latitude, longitude, iot_token, owner_id FROM warehouses WHERE warehouse_id = ?",
            (warehouse_id,)
        )
        wh = cursor.fetchone()
        
        if wh:
            # 4. Ajouter à my_warehouse
            cursor.execute(
                "INSERT OR REPLACE INTO my_warehouse (id_entrepot, researcher_id, nom, adresse, latitude, longitude, iot_token, product_name) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (warehouse_id, uid, wh["name"], wh["address"], wh["latitude"], wh["longitude"], wh["iot_token"], product_name)
            )
            
            # 5. Marquer l'entrepôt comme LOUÉ
            cursor.execute(
                "UPDATE warehouses SET status = 'rented' WHERE warehouse_id = ?",
                (warehouse_id,)
            )

            # NOTIFICATION EMAIL AU PROPRIÉTAIRE (EN ARRIÈRE-PLAN)
            try:
                cursor.execute("SELECT email FROM users WHERE user_id = ?", (wh["owner_id"],))
                owner_row = cursor.fetchone()
                
                cursor.execute("SELECT full_name FROM users WHERE user_id = ?", (uid,))
                researcher_row = cursor.fetchone()
                
                if owner_row and researcher_row:
                    background_tasks.add_task(
                        send_acceptance_confirmation_email,
                        owner_row["email"], 
                        researcher_row["full_name"], 
                        wh["name"]
                    )
            except Exception as email_err:
                print(f"Erreur préparation email acceptation : {email_err}")
        
        conn.commit()
        return {"message": "Offre acceptée ! L'accès IoT est maintenant débloqué dans 'Mes Entrepôts'."}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur technique : {str(e)}")
    finally:
        conn.close()
from core.messaging import delete_contact_request

@router.delete("/request/{request_id}")
def delete_request(request_id: str, current_user: dict = Depends(get_current_user)):
    ok = delete_contact_request(request_id, int(current_user["user_id"]))
    if not ok:
        raise HTTPException(status_code=404, detail="Demande introuvable ou vous n'avez pas le droit de la supprimer.")
    return {"message": "Historique supprimé avec succès."}
