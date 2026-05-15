import sqlite3
import uuid

import pandas as pd

from utils.db import DB_PATH, get_db_connection, load_sql_to_dataframe


REQUEST_PENDING = "pending"
REQUEST_ACCEPTED = "accepted"
REQUEST_REJECTED = "rejected"


def _connect():
    """Connexion SQLite WAL-safe pour le module messaging."""
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 30000")
    return conn


def ensure_messaging_schema() -> None:
    conn = _connect()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS contact_requests (
            request_id TEXT PRIMARY KEY,
            warehouse_id TEXT NOT NULL,
            owner_id INTEGER NOT NULL,
            researcher_id INTEGER NOT NULL,
            product_name TEXT,
            message TEXT,
            status TEXT NOT NULL DEFAULT 'pending'
                CHECK(status IN ('pending', 'accepted', 'rejected')),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id) ON DELETE CASCADE,
            FOREIGN KEY (owner_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (researcher_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_messages (
            message_id TEXT PRIMARY KEY,
            request_id TEXT NOT NULL,
            sender_id INTEGER NOT NULL,
            sender_role TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (request_id) REFERENCES contact_requests(request_id) ON DELETE CASCADE
        )
        """
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_contact_requests_owner ON contact_requests(owner_id, status)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_contact_requests_researcher ON contact_requests(researcher_id, status)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_chat_messages_request ON chat_messages(request_id, created_at)"
    )
    conn.commit()
    conn.close()


def create_contact_request(
    warehouse_id: str,
    owner_id: int,
    researcher_id: int,
    product_name: str,
    message: str,
) -> tuple[bool, str]:
    ensure_messaging_schema()

    # Vérifier si une demande active existe déjà pour ce trio
    existing = load_sql_to_dataframe(
        """
        SELECT request_id, status
        FROM contact_requests
        WHERE warehouse_id = ? AND owner_id = ? AND researcher_id = ?
        ORDER BY datetime(created_at) DESC
        LIMIT 1
        """,
        (warehouse_id, owner_id, researcher_id),
    )
    if not existing.empty and existing.iloc[0]["status"] in [REQUEST_PENDING, REQUEST_ACCEPTED]:
        return False, "Une demande de discussion est deja en cours pour cet entrepot."

    # Vérifier que le researcher_id existe bien dans la DB
    researcher_check = load_sql_to_dataframe(
        "SELECT user_id FROM users WHERE user_id = ?", (researcher_id,)
    )
    if researcher_check.empty:
        print(f"[ERREUR] create_contact_request: researcher_id={researcher_id} introuvable en DB")
        return False, f"Erreur interne : votre compte (ID={researcher_id}) n'est pas reconnu. Reconnectez-vous."

    # Vérifier que l'owner_id existe
    owner_check = load_sql_to_dataframe(
        "SELECT user_id FROM users WHERE user_id = ?", (owner_id,)
    )
    if owner_check.empty:
        print(f"[ERREUR] create_contact_request: owner_id={owner_id} introuvable en DB")
        return False, f"Erreur interne : le propriétaire (ID={owner_id}) n'est pas reconnu."

    request_id = str(uuid.uuid4())[:8]
    try:
        conn = _connect()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO contact_requests (
                request_id, warehouse_id, owner_id, researcher_id, product_name, message, status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (request_id, warehouse_id, owner_id, researcher_id, product_name, message.strip(), REQUEST_PENDING),
        )
        # 3. Insérer le message initial dans le chat pour qu'il soit visible dès l'ouverture
        cursor.execute(
            """
            INSERT INTO chat_messages (message_id, request_id, sender_id, sender_role, message)
            VALUES (?, ?, ?, ?, ?)
            """,
            (str(uuid.uuid4())[:8], request_id, researcher_id, "researcher", message.strip()),
        )

        cursor.execute(
            "UPDATE warehouses SET status = 'locked' WHERE warehouse_id = ?",
            (warehouse_id,)
        )
        conn.commit()
        conn.close()
        print(f"[OK] Demande {request_id} créée, message initial inséré et entrepôt {warehouse_id} VERROUILLÉ.")
        return True, request_id
    except Exception as e:
        print(f"[ERREUR] Insertion contact_request: {e}")
        return False, f"Erreur serveur lors de l'envoi de la demande : {e}"



def get_researcher_requests(researcher_id: int) -> pd.DataFrame:
    ensure_messaging_schema()
    return load_sql_to_dataframe(
        """
        SELECT
            cr.request_id,
            cr.warehouse_id,
            w.name AS warehouse_name,
            w.address AS warehouse_address,
            cr.owner_id,
            u.first_name AS owner_first_name,
            cr.product_name,
            cr.message,
            cr.status,
            cr.created_at,
            cr.updated_at
        FROM contact_requests cr
        LEFT JOIN warehouses w ON w.warehouse_id = cr.warehouse_id
        LEFT JOIN users u ON u.user_id = cr.owner_id
        WHERE cr.researcher_id = ?
        ORDER BY datetime(cr.created_at) DESC
        """,
        (researcher_id,),
    )


def get_owner_requests(owner_id: int) -> pd.DataFrame:
    ensure_messaging_schema()
    return load_sql_to_dataframe(
        """
        SELECT
            cr.request_id,
            cr.warehouse_id,
            w.name AS warehouse_name,
            w.address AS warehouse_address,
            cr.researcher_id,
            u.first_name AS researcher_first_name,
            cr.product_name,
            cr.message,
            cr.status,
            cr.created_at,
            cr.updated_at
        FROM contact_requests cr
        LEFT JOIN warehouses w ON w.warehouse_id = cr.warehouse_id
        LEFT JOIN users u ON u.user_id = cr.researcher_id
        WHERE cr.owner_id = ?
        ORDER BY datetime(cr.created_at) DESC
        """,
        (owner_id,),
    )


def update_contact_request_status(request_id: str, owner_id: int, new_status: str) -> bool:
    ensure_messaging_schema()
    if new_status not in [REQUEST_ACCEPTED, REQUEST_REJECTED]:
        return False

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE contact_requests
        SET status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE request_id = ? AND owner_id = ?
        """,
        (new_status, request_id, owner_id),
    )
    conn.commit()
    changed = cursor.rowcount > 0
    conn.close()
    return changed


def get_chat_messages(request_id: str) -> pd.DataFrame:
    ensure_messaging_schema()
    return load_sql_to_dataframe(
        """
        SELECT request_id, sender_id, sender_role, message, created_at
        FROM chat_messages
        WHERE request_id = ?
        ORDER BY datetime(created_at) ASC
        """,
        (request_id,),
    )


def send_chat_message(request_id: str, sender_id: int, sender_role: str, message: str) -> tuple[bool, str]:
    ensure_messaging_schema()
    cleaned_message = message.strip()
    if not cleaned_message:
        return False, "Le message est vide."

    req = load_sql_to_dataframe(
        "SELECT status FROM contact_requests WHERE request_id = ?",
        (request_id,),
    )
    if req.empty:
        return False, "Demande introuvable."
    if req.iloc[0]["status"] != REQUEST_ACCEPTED:
        return False, "La messagerie n'est disponible qu'apres acceptation."

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO chat_messages (message_id, request_id, sender_id, sender_role, message)
        VALUES (?, ?, ?, ?, ?)
        """,
        (str(uuid.uuid4())[:8], request_id, sender_id, sender_role, cleaned_message),
    )
    conn.commit()
    conn.close()
    return True, "Message envoye."


def create_rental_offer(request_id: str, owner_id: int, price: float, start_date: str) -> tuple[bool, str]:
    """Cree une offre de location (reservation pending) et envoie un message special."""
    ensure_messaging_schema()
    
    # Recupérer les infos de la demande
    req = load_sql_to_dataframe(
        "SELECT warehouse_id, researcher_id FROM contact_requests WHERE request_id = ? AND owner_id = ?",
        (request_id, owner_id),
    )
    if req.empty:
        return False, "Demande introuvable ou vous n'etes pas le proprietaire."
    
    warehouse_id = req.iloc[0]["warehouse_id"]
    researcher_id = int(req.iloc[0]["researcher_id"])
    
    # Verifier si une offre existe deja
    existing = load_sql_to_dataframe(
        "SELECT reservation_id FROM reservations WHERE warehouse_id = ? AND researcher_id = ? AND status = 'pending'",
        (warehouse_id, researcher_id),
    )
    if not existing.empty:
        return False, "Une offre est deja en attente pour cet entrepot."
    
    res_id = str(uuid.uuid4())[:8]
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO reservations (reservation_id, warehouse_id, researcher_id, global_score, status, reason)
            VALUES (?, ?, ?, ?, 'pending', ?)
            """,
            (res_id, warehouse_id, researcher_id, float(price), str(start_date)),
        )
        conn.commit()
        conn.close()
        
        # Envoyer le message de notification dans le chat
        msg_text = f"🏢 **OFFRE DE LOCATION**\n\n💰 Prix proposé : **{price} DH**\n📅 Date de début : **{start_date}**\n\n*(Vous pouvez accepter cette offre pour débloquer l'accès IoT)*"
        send_chat_message(request_id, owner_id, "owner", msg_text)
        
        return True, "Offre envoyée avec succès."
    except Exception as e:
        return False, f"Erreur lors de la création de l'offre : {e}"


def check_warehouse_access(warehouse_id: str, user_id: int, role: str) -> bool:
    """Verifie si un utilisateur a le droit d'acceder aux donnees IoT d'un entrepot."""
    if role == "owner":
        # Le proprietaire a toujours accès à ses propres entrepôts
        check = load_sql_to_dataframe(
            "SELECT 1 FROM warehouses WHERE warehouse_id = ? AND owner_id = ?",
            (warehouse_id, user_id),
        )
        return not check.empty
    elif role == "researcher":
        # Le chercheur a accès si il a une reservation CONFIRMED
        check = load_sql_to_dataframe(
            "SELECT 1 FROM reservations WHERE warehouse_id = ? AND researcher_id = ? AND status = 'confirmed'",
            (warehouse_id, user_id),
        )
        return not check.empty
    return False


def delete_contact_request(request_id: str, user_id: int) -> bool:
    """Supprime une demande et ses messages si l'utilisateur est concerné."""
    ensure_messaging_schema()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Verifier si l'utilisateur est le chercheur ou le proprio
    cursor.execute(
        "SELECT 1 FROM contact_requests WHERE request_id = ? AND (owner_id = ? OR researcher_id = ?)",
        (request_id, user_id, user_id)
    )
    if not cursor.fetchone():
        conn.close()
        return False
        
    # Supprimer les messages et la demande
    cursor.execute("DELETE FROM chat_messages WHERE request_id = ?", (request_id,))
    cursor.execute("DELETE FROM contact_requests WHERE request_id = ?", (request_id,))
    
    conn.commit()
    conn.close()
    return True
