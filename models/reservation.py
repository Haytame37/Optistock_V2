"""
models/reservation.py
═══════════════════════════════════════════════════════════════════════════════
Modèle de données pour les réservations d'entrepôts OptiStock.

System_Pre_Lock — Mécanisme de verrouillage applicatif :
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
from typing import ClassVar, Optional

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

    _verrous_actifs: ClassVar[dict] = {}

    def appliquer_verrou(self, warehouse_id: str) -> dict:
        maintenant = datetime.now()
        self._purger_verrous_expires()

        verrou_existant = Reservation._verrous_actifs.get(warehouse_id)
        if verrou_existant is not None:
            expiration = verrou_existant["expires_at"]
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
                        f"(chercheur: {verrou_existant['researcher_id']}). "
                        f"Expire dans {temps_restant} min."
                    ),
                }

        expiration = maintenant + timedelta(minutes=DUREE_VERROU_MINUTES)
        self.warehouse_id = warehouse_id
        self.status       = STATUS_PRE_LOCK
        self.expires_at   = expiration

        Reservation._verrous_actifs[warehouse_id] = {
            "reservation_id": self.reservation_id,
            "researcher_id":  self.researcher_id,
            "created_at":     maintenant,
            "expires_at":     expiration,
            "status":         STATUS_PRE_LOCK,
            "global_score":   self.global_score,
        }

        return {
            "succes":         True,
            "status":         STATUS_PRE_LOCK,
            "warehouse_id":   warehouse_id,
            "expires_at":     expiration,
            "duree_restante": DUREE_VERROU_MINUTES,
            "message": f"🔒 Entrepôt '{warehouse_id}' verrouillé pour {DUREE_VERROU_MINUTES} min.",
        }

    def liberer_verrou(self, warehouse_id: str) -> dict:
        if warehouse_id in Reservation._verrous_actifs:
            del Reservation._verrous_actifs[warehouse_id]
            self.status     = STATUS_CANCELED
            self.expires_at = None
            self.reason     = "Libération manuelle"
            return {"succes": True, "message": f"🔓 Verrou sur '{warehouse_id}' libéré."}
        return {"succes": False, "message": f"ℹ️ Aucun verrou actif sur '{warehouse_id}'."}

    def confirmer_reservation(self) -> dict:
        if self.status != STATUS_PRE_LOCK:
            return {"succes": False, "message": f"❌ Impossible de confirmer : statut actuel '{self.status}'."}
        self.status = STATUS_CONFIRMED
        Reservation._verrous_actifs.pop(self.warehouse_id, None)
        return {"succes": True, "message": f"✅ Réservation {self.reservation_id} CONFIRMÉE."}

    @classmethod
    def get_verrous_actifs(cls) -> dict:
        cls._purger_verrous_expires_cls()
        return dict(cls._verrous_actifs)

    @classmethod
    def get_statut_entrepot(cls, warehouse_id: str) -> str:
        cls._purger_verrous_expires_cls()
        if warehouse_id in cls._verrous_actifs:
            return STATUS_PRE_LOCK
        return STATUS_AVAILABLE

    @classmethod
    def _purger_verrous_expires_cls(cls) -> int:
        maintenant = datetime.now()
        expires = [wh_id for wh_id, v in cls._verrous_actifs.items() if v["expires_at"] <= maintenant]
        for wh_id in expires:
            del cls._verrous_actifs[wh_id]
        return len(expires)

    def _purger_verrous_expires(self) -> int:
        return Reservation._purger_verrous_expires_cls()

    def __repr__(self) -> str:
        return f"Reservation(id={self.reservation_id!r}, warehouse={self.warehouse_id!r}, status={self.status!r})"
