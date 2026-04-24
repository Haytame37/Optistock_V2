"""
models/reservation.py
═══════════════════════════════════════════════════════════════════════════════
Modèle de données pour les réservations d'entrepôts OptiStock.

System_Pre_Lock — Mécanisme de verrouillage applicatif persistant (SQLite) :
    Avant de finaliser un contrat, une fenêtre de négociation de 15 minutes
    est ouverte pendant laquelle l'entrepôt est placé en statut 'pre_lock'.
    Cela évite les réservations CONCURRENTES sur le même espace.

    Cycle de vie d'une réservation :
        AVAILABLE → (négociation) → PRE_LOCK → CONFIRMED
                                           ↘ CANCELED (timeout/manuel)
═══════════════════════════════════════════════════════════════════════════════
"""

from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional

from utils.db import execute_query, load_sql_to_dataframe

DUREE_VERROU_MINUTES: int = 15

STATUS_AVAILABLE = "available"
STATUS_PRE_LOCK  = "pre_lock"
STATUS_CONFIRMED = "confirmed"
STATUS_CANCELED  = "canceled"

@dataclass
class Reservation:
    reservation_id:  str
    warehouse_id:    str
    researcher_id:   int
    global_score:    float              = 0.0
    status:          str                = STATUS_AVAILABLE
    created_at:      datetime           = field(default_factory=datetime.now)
    expires_at:      Optional[datetime] = None
    reason:          str                = ""

    def appliquer_verrou(self, warehouse_id: str) -> dict:
        self._purger_verrous_expires()
        
        # Vérification d'un verrou existant non expiré dans la DB
        query = f"SELECT * FROM reservations WHERE warehouse_id = '{warehouse_id}' AND status IN ('{STATUS_PRE_LOCK}', '{STATUS_CONFIRMED}')"
        df_actifs = load_sql_to_dataframe(query)
        
        maintenant = datetime.now()
        
        for _, row in df_actifs.iterrows():
            expiration_str = row.get("expires_at")
            if pd.notna(expiration_str) and expiration_str:
                expiration = pd.to_datetime(expiration_str)
                if expiration > maintenant:
                    temps_restant = max(1, int((expiration - maintenant).total_seconds() / 60) + 1)
                    return {
                        "succes":         False,
                        "status":         "ALREADY_LOCKED",
                        "warehouse_id":   warehouse_id,
                        "expires_at":     expiration,
                        "duree_restante": temps_restant,
                        "message": (
                            f"⛔ L'entrepôt '{warehouse_id}' est déjà verrouillé "
                            f"(chercheur: {row['researcher_id']}). "
                            f"Expire dans {temps_restant} min."
                        ),
                    }

        # Création du nouveau verrou dans la DB
        expiration = maintenant + timedelta(minutes=DUREE_VERROU_MINUTES)
        self.warehouse_id = warehouse_id
        self.status       = STATUS_PRE_LOCK
        self.expires_at   = expiration

        execute_query(
            "INSERT INTO reservations (reservation_id, warehouse_id, researcher_id, global_score, status, reason, created_at, expires_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (self.reservation_id, self.warehouse_id, self.researcher_id, self.global_score, self.status, self.reason, maintenant.strftime('%Y-%m-%d %H:%M:%S'), expiration.strftime('%Y-%m-%d %H:%M:%S'))
        )
        
        # Mettre à jour le statut de l'entrepôt
        execute_query(f"UPDATE warehouses SET status = 'locked' WHERE warehouse_id = '{warehouse_id}'")

        return {
            "succes":         True,
            "status":         STATUS_PRE_LOCK,
            "warehouse_id":   warehouse_id,
            "expires_at":     expiration,
            "duree_restante": DUREE_VERROU_MINUTES,
            "message": f"🔒 Entrepôt '{warehouse_id}' verrouillé pour {DUREE_VERROU_MINUTES} min.",
        }

    def liberer_verrou(self, warehouse_id: str) -> dict:
        query = f"SELECT * FROM reservations WHERE warehouse_id = '{warehouse_id}' AND status = '{STATUS_PRE_LOCK}'"
        df = load_sql_to_dataframe(query)
        if not df.empty:
            execute_query(f"UPDATE reservations SET status = '{STATUS_CANCELED}', reason = 'Libération manuelle' WHERE warehouse_id = '{warehouse_id}' AND status = '{STATUS_PRE_LOCK}'")
            execute_query(f"UPDATE warehouses SET status = 'available' WHERE warehouse_id = '{warehouse_id}'")
            self.status     = STATUS_CANCELED
            self.expires_at = None
            self.reason     = "Libération manuelle"
            return {"succes": True, "message": f"🔓 Verrou sur '{warehouse_id}' libéré."}
        return {"succes": False, "message": f"ℹ️ Aucun verrou actif sur '{warehouse_id}'."}

    def confirmer_reservation(self) -> dict:
        query = f"SELECT * FROM reservations WHERE reservation_id = '{self.reservation_id}' AND status = '{STATUS_PRE_LOCK}'"
        df = load_sql_to_dataframe(query)
        if df.empty:
            return {"succes": False, "message": f"❌ Impossible de confirmer : réservation non trouvée ou non pré-verrouillée."}
            
        execute_query(f"UPDATE reservations SET status = '{STATUS_CONFIRMED}' WHERE reservation_id = '{self.reservation_id}'")
        execute_query(f"UPDATE warehouses SET status = 'unavailable' WHERE warehouse_id = '{self.warehouse_id}'")
        self.status = STATUS_CONFIRMED
        return {"succes": True, "message": f"✅ Réservation {self.reservation_id} CONFIRMÉE."}

    @classmethod
    def get_verrous_actifs(cls) -> dict:
        cls._purger_verrous_expires_cls()
        df = load_sql_to_dataframe(f"SELECT * FROM reservations WHERE status = '{STATUS_PRE_LOCK}'")
        verrous = {}
        for _, row in df.iterrows():
            exp_str = row.get("expires_at")
            exp_date = pd.to_datetime(exp_str) if pd.notna(exp_str) else None
            verrous[row["warehouse_id"]] = {
                "reservation_id": row["reservation_id"],
                "researcher_id": row["researcher_id"],
                "status": row["status"],
                "expires_at": exp_date
            }
        return verrous

    @classmethod
    def get_statut_entrepot(cls, warehouse_id: str) -> str:
        cls._purger_verrous_expires_cls()
        df = load_sql_to_dataframe(f"SELECT status FROM warehouses WHERE warehouse_id = '{warehouse_id}'")
        if not df.empty:
            st = df.iloc[0]["status"]
            return STATUS_PRE_LOCK if st == "locked" else st
        return STATUS_AVAILABLE

    @classmethod
    def _purger_verrous_expires_cls(cls) -> int:
        maintenant = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # On trouve les réservations expirées
        df = load_sql_to_dataframe(f"SELECT warehouse_id FROM reservations WHERE status = '{STATUS_PRE_LOCK}' AND expires_at <= '{maintenant}'")
        if not df.empty:
            execute_query(f"UPDATE reservations SET status = '{STATUS_CANCELED}', reason = 'Timeout' WHERE status = '{STATUS_PRE_LOCK}' AND expires_at <= '{maintenant}'")
            # Libérer les entrepôts
            for _, row in df.iterrows():
                execute_query(f"UPDATE warehouses SET status = 'available' WHERE warehouse_id = '{row['warehouse_id']}'")
            return len(df)
        return 0

    def _purger_verrous_expires(self) -> int:
        return Reservation._purger_verrous_expires_cls()

    def __repr__(self) -> str:
        return f"Reservation(id={self.reservation_id!r}, warehouse={self.warehouse_id!r}, status={self.status!r})"

import pandas as pd
