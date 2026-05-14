from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional

from services.chatbot_service import OptiBotService
from dependencies.auth import decode_token
from utils.db import load_sql_to_dataframe

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)

security = HTTPBearer(auto_error=False)


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []
    current_path: Optional[str] = "/"


class ChatResponse(BaseModel):
    response: str


@router.post("/", response_model=ChatResponse)
async def chat_with_optibot(
    request: ChatRequest,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """
    Endpoint pour interagir avec OptiBot de manière dynamique.
    """
    role = "public"

    # Si on est sur l'accueil, on force le rôle public, peu importe qui est connecté
    if request.current_path in ["/", "/login", "/register", "/about"]:
        role = "public"
    elif credentials:
        payload = decode_token(credentials.credentials)
        if payload and payload.get("type") == "access":
            user_id = payload.get("sub")
            if user_id:
                df = load_sql_to_dataframe(
                    "SELECT role FROM users WHERE user_id = ? AND is_active = 1",
                    (int(user_id),),
                )
                if not df.empty:
                    role = df.iloc[0]["role"]

    bot_service = OptiBotService(role=role)

    user_id_val = None
    if credentials:
        payload = decode_token(credentials.credentials)
        if payload and payload.get("type") == "access":
            user_id_val = payload.get("sub")

    context_data = ""
    
    if role == "owner" and user_id_val:
        try:
            # Entrepôts possédés
            warehouses_df = load_sql_to_dataframe("SELECT name FROM warehouses WHERE owner_id = ?", (user_id_val,))
            warehouses = warehouses_df['name'].tolist() if not warehouses_df.empty else []
            
            # Messages en attente
            msgs_df = load_sql_to_dataframe(
                '''SELECT m.status, u.first_name as researcher_first_name, w.name as warehouse_name
                   FROM messages m
                   JOIN users u ON m.sender_id = u.user_id
                   JOIN warehouses w ON m.warehouse_id = w.warehouse_id
                   WHERE m.receiver_id = ? AND m.status = 'pending' ''',
                (user_id_val,)
            )
            
            pending_count = len(msgs_df) if not msgs_df.empty else 0
            pending_details = []
            if not msgs_df.empty:
                for _, row in msgs_df.iterrows():
                    pending_details.append(f"- De {row.get('researcher_first_name', 'Chercheur')} pour '{row.get('warehouse_name', '')}'")

            context_data = "--- DONNÉES EN TEMPS RÉEL DU PROPRIÉTAIRE ---\n"
            context_data += f"Entrepôts possédés : {len(warehouses)}\n"
            if warehouses:
                context_data += f"Liste : {', '.join(warehouses)}\n"
            context_data += f"Nouveaux messages en attente : {pending_count}\n"
            if pending_details:
                context_data += "\n".join(pending_details) + "\n"
                
            context_data += "\n--- INSTRUCTIONS D'INTERFACE ---\n"
            context_data += "- S'il demande 'comment ajouter un entrepôt', dis-lui de cliquer sur 'Démarrer la configuration' sur le tableau de bord ou d'aller dans 'Ajout Entrepôt' via le menu.\n"
            context_data += "- S'il demande 'comment gérer un entrepôt', dis-lui d'aller dans l'onglet 'Liste Entrepôts'.\n"
            context_data += "- S'il veut répondre/lire ses messages, dis-lui de cliquer sur 'Ouvrir la messagerie' dans le tableau de bord.\n"
            context_data += "--------------------------------------\n"
        except Exception as e:
            print(f"Erreur récupération contexte owner: {e}")

    elif role == "researcher" and user_id_val:
        try:
            # Messages/Demandes
            msgs_df = load_sql_to_dataframe(
                '''SELECT m.status, u.first_name as owner_first_name, w.name as warehouse_name
                   FROM messages m
                   JOIN users u ON m.receiver_id = u.user_id
                   JOIN warehouses w ON m.warehouse_id = w.warehouse_id
                   WHERE m.sender_id = ?''',
                (user_id_val,)
            )
            
            pending_details = []
            accepted_details = []
            if not msgs_df.empty:
                for _, row in msgs_df.iterrows():
                    if row["status"] == "pending":
                        pending_details.append(f"- '{row.get('warehouse_name', '')}' (En attente de validation)")
                    elif row["status"] == "accepted":
                        accepted_details.append(f"- '{row.get('warehouse_name', '')}' (Acceptée par {row.get('owner_first_name', 'le propriétaire')})")
                        
            # Historique de recherche
            history_df = load_sql_to_dataframe(
                "SELECT product_name, volume, created_at FROM search_history WHERE researcher_id = ? ORDER BY created_at DESC LIMIT 3",
                (user_id_val,)
            )
            recent_searches = []
            if not history_df.empty:
                for _, row in history_df.iterrows():
                    recent_searches.append(f"- Produit: {row['product_name']}, Volume: {row['volume']} m³")

            # Produits disponibles
            available_products = []
            try:
                from utils.product_conditions import PRODUCT_CONDITIONS
                available_products = list(PRODUCT_CONDITIONS.keys())
            except Exception:
                pass

            context_data = "--- DONNÉES EN TEMPS RÉEL DU CHERCHEUR ---\n"
            if available_products:
                context_data += f"Produits qu'il est possible de rechercher sur la plateforme : {', '.join(available_products)}\n"
                context_data += "⚠️ RÈGLE ABSOLUE : Si le chercheur mentionne un produit qui n'est PAS dans cette liste (par exemple 'pomme de terre', 'voiture', etc.), TU DOIS REFUSER L'ANALYSE en lui disant EXACTEMENT : \"Pour ce produit, on ne peut pas te trouver un entrepôt idéal côté environnement.\"\n"
                
            context_data += f"Demandes de location en attente : {len(pending_details)}\n"
            if pending_details:
                context_data += "\n".join(pending_details) + "\n"
            context_data += f"Demandes de location acceptées (Réponses des propriétaires) : {len(accepted_details)}\n"
            if accepted_details:
                context_data += "\n".join(accepted_details) + "\n"
                
            if recent_searches:
                context_data += "\nDernières recherches d'entrepôts effectuées :\n"
                context_data += "\n".join(recent_searches) + "\n"
                
            context_data += "\n--- INSTRUCTIONS D'INTERFACE ---\n"
            context_data += "- S'il demande 'comment chercher un entrepôt', dis-lui d'aller dans l'onglet 'Chercheur IA' ou 'Dashboard Chercheur'.\n"
            context_data += "- S'il demande à voir les réponses des propriétaires, dis-lui d'aller dans l'onglet 'Messagerie'.\n"
            context_data += "⚠️ RÈGLE DE SAISIE DE RECHERCHE : L'interface de recherche NE DEMANDE QUE 3 INFORMATIONS au chercheur : 1) Le Produit (liste déroulante), 2) Le Volume (m³), et 3) La Durée (jours). Le système OptiStock calcule automatiquement les besoins en température et humidité en arrière-plan. NE DEMANDE JAMAIS au chercheur des données supplémentaires (température, zone géographique, poids, etc.) car il n'y a pas de champs pour les saisir !\n"
            context_data += "--------------------------------------\n"
        except Exception as e:
            print(f"Erreur récupération contexte researcher: {e}")

    history_dict = [{"role": msg.role, "content": msg.content} for msg in request.history]

    response_text = bot_service.get_response(
        user_input=request.message,
        app_history=history_dict,
        context_data=context_data
    )

    return ChatResponse(response=response_text)
