import streamlit as st
from utils.chatbot_utils import OptiBot

import streamlit.components.v1 as components

def render_optibot():
    """
    Rendu du chatbot flottant OptiBot avec st.popover (Natif Streamlit).
    Positionnement fixe avec Drag & Drop robuste et mémorisation.
    """
    # 1. Styles CSS localisés
    st.markdown("""
    <style>
    /* Cibler le conteneur global du popover pour le positionnement */
    .optibot-floating-container {
        position: fixed !important;
        top: 70px !important;
        right: 25px !important;
        z-index: 999999 !important;
        width: 60px !important;
        height: 60px !important;
    }

    /* Le style du bouton à l'intérieur du conteneur */
    .optibot-floating-container button {
        width: 100% !important;
        height: 100% !important;
        border-radius: 50% !important;
        background-color: #005da7 !important;
        color: white !important;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3) !important;
        border: 2px solid white !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 28px !important;
        transition: transform 0.2s;
        padding: 0 !important;
    }
    .optibot-floating-container button:hover {
        transform: scale(1.1);
    }
    .optibot-floating-container p {
        margin: 0 !important;
        font-size: 28px !important;
    }

    /* Style du contenu du Popover */
    div[data-testid="stPopoverBody"] {
        background: white !important;
        border-radius: 20px !important;
        box-shadow: 0 15px 50px rgba(0, 0, 0, 0.3) !important;
        width: 380px !important;
        border: 1px solid #ddd !important;
        padding: 0 !important;
    }

    .optibot-header-native {
        background-color: #005da7 !important;
        color: white !important;
        padding: 15px 20px !important;
        font-weight: bold !important;
        font-size: 16px !important;
        border-radius: 20px 20px 0 0 !important;
        margin-bottom: 10px;
    }

    .bot-row-v15 {
        display: flex;
        gap: 12px;
        padding: 10px 15px;
        align-items: flex-start;
    }

    .bot-icon-v15 {
        background-color: #ff9800;
        border-radius: 8px;
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        flex-shrink: 0;
    }

    .bot-text-v15 {
        color: #333;
        font-size: 14px;
        line-height: 1.5;
        font-family: 'Inter', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

    # 2. Identifier le rôle de l'utilisateur
    current_role = "public"
    if st.session_state.get('logged_in'):
        current_role = st.session_state.get('role') or st.session_state.get('user', {}).get('role', 'public')

    # Session State par rôle (pour ne pas mélanger les conversations)
    session_key = f"messages_{current_role}"
    if session_key not in st.session_state:
        welcome_msgs = {
            "owner": "🏭 Bonjour Propriétaire ! Je suis là pour vous aider à gérer vos entrepôts et vos locations.",
            "researcher": "🔬 Bonjour Chercheur ! Besoin d'aide pour trouver l'entrepôt idéal ou calculer un score d'optimisation ?",
            "admin": "⚙️ Bonjour Admin ! Prêt à superviser la plateforme OptiStock ?",
            "public": "👋 Bonjour ! Je suis OptiBot. Posez-moi vos questions sur nos services de stockage IoT !"
        }
        st.session_state[session_key] = [
            {"role": "assistant", "content": welcome_msgs.get(current_role, welcome_msgs["public"])}
        ]

    # 3. Rendu avec st.popover
    with st.popover("🤖", use_container_width=False):
        st.markdown('<div class="optibot-header-native">OptiBot Assistant</div>', unsafe_allow_html=True)
        
        with st.container(height=350, border=False):
            for msg in st.session_state[session_key]:
                if msg["role"] == "assistant":
                    st.markdown(f"""
                        <div class="bot-row-v15">
                            <div class="bot-icon-v15">🤖</div>
                            <div class="bot-text-v15">{msg['content']}</div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    with st.chat_message("user"):
                        st.markdown(msg["content"])
        
        with st.form(key="chat_form_native", clear_on_submit=True):
            c1, c2 = st.columns([5, 1])
            with c1:
                st.text_input("Message", placeholder="Posez votre question...", label_visibility="collapsed", key="u_in_native")
            with c2:
                if st.form_submit_button("▲"):
                    u_in = st.session_state.u_in_native
                    if u_in:
                        # 1. Construction du contexte dynamique en temps réel
                        context_data = ""
                        
                        if current_role == "owner":
                            user_id = st.session_state.get('user_id') or st.session_state.get('user', {}).get('user_id')
                            if user_id:
                                try:
                                    from core.warehouse_service import get_warehouses_by_owner
                                    from core.messaging import get_owner_requests
                                    
                                    # Récupération des entrepôts
                                    warehouses = get_warehouses_by_owner(user_id)
                                    wh_names = [w['name'] for w in warehouses] if warehouses else []
                                    
                                    # Récupération des messages
                                    msgs = get_owner_requests(user_id)
                                    pending_count = 0
                                    pending_details = []
                                    if not msgs.empty:
                                        pending_df = msgs[msgs["status"] == "pending"]
                                        pending_count = len(pending_df)
                                        for _, row in pending_df.iterrows():
                                            pending_details.append(f"- De {row.get('researcher_first_name', 'Chercheur')} pour '{row.get('warehouse_name', '')}'")
                                            
                                    context_data = "--- DONNÉES EN TEMPS RÉEL DU PROPRIÉTAIRE ---\n"
                                    context_data += f"Entrepôts possédés : {len(warehouses)}\n"
                                    if wh_names:
                                        context_data += f"Liste : {', '.join(wh_names)}\n"
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

                        elif current_role == "researcher":
                            user_id = st.session_state.get('user_id') or st.session_state.get('user', {}).get('user_id')
                            if user_id:
                                try:
                                    from utils.db import load_sql_to_dataframe
                                    from core.messaging import get_researcher_requests
                                    
                                    # Messages/Demandes
                                    msgs = get_researcher_requests(user_id)
                                    pending_details = []
                                    accepted_details = []
                                    if not msgs.empty:
                                        for _, row in msgs.iterrows():
                                            if row["status"] == "pending":
                                                pending_details.append(f"- '{row.get('warehouse_name', '')}' (En attente de validation)")
                                            elif row["status"] == "accepted":
                                                accepted_details.append(f"- '{row.get('warehouse_name', '')}' (Acceptée par {row.get('owner_first_name', 'le propriétaire')})")
                                                
                                    # Historique de recherche
                                    history_df = load_sql_to_dataframe(
                                        "SELECT product_name, volume, created_at FROM search_history WHERE researcher_id = ? ORDER BY created_at DESC LIMIT 3",
                                        (user_id,)
                                    )
                                    recent_searches = []
                                    if not history_df.empty:
                                        for _, row in history_df.iterrows():
                                            recent_searches.append(f"- Produit: {row['product_name']}, Volume: {row['volume']} m³")

                                    # Liste des produits disponibles pour la recherche
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

                        # 2. On clone l'historique actuel pour l'envoyer comme contexte (avant d'ajouter le nouveau message utilisateur)
                        current_history = list(st.session_state[session_key])
                        
                        st.session_state[session_key].append({"role": "user", "content": u_in})
                        bot = OptiBot(role=current_role)
                        
                        # 3. On envoie l'input + l'historique complet + le contexte dynamique
                        bot_response = bot.get_response(u_in, app_history=current_history, context_data=context_data)
                        st.session_state[session_key].append({"role": "assistant", "content": bot_response})
                        st.rerun()

    # 4. Petit script JS pour appliquer la classe fixe et le drag-and-drop au conteneur du popover
    components.html("""
        <script>
        function stylePopoverButton() {
            try {
                const doc = window.parent.document;
                const buttons = doc.querySelectorAll('button');
                
                buttons.forEach(btn => {
                    if (btn.innerText.includes("🤖")) {
                        // Trouver le conteneur parent du popover (Streamlit l'enveloppe toujours)
                        // On remonte jusqu'à un div qui a la classe stPopover ou on prend juste un parent proche
                        let container = btn.closest('div[data-testid="stPopover"]');
                        
                        // Fallback si stPopover n'existe pas
                        if (!container) {
                            container = btn.parentElement;
                        }

                        if (container && !container.classList.contains('optibot-floating-container')) {
                            container.classList.add('optibot-floating-container');
                            btn.style.cursor = 'move';
                        
                        // --- Logique de Drag and Drop avec CSS Transform ---
                        if (!container.dataset.dragSet) {
                            container.dataset.dragSet = "true";
                            
                            let isDragging = false;
                            let hasDragged = false;
                            
                            let currentX = 0;
                            let currentY = 0;
                            let initialX = 0;
                            let initialY = 0;
                            let xOffset = 0;
                            let yOffset = 0;

                            // 1. Restaurer la position depuis le localStorage
                            const savedX = localStorage.getItem('optibot_x');
                            const savedY = localStorage.getItem('optibot_y');
                            if (savedX && savedY) {
                                xOffset = parseFloat(savedX);
                                yOffset = parseFloat(savedY);
                                container.style.transform = `translate3d(${xOffset}px, ${yOffset}px, 0)`;
                            }

                            // 2. Gestion des événements
                            btn.addEventListener('mousedown', (e) => {
                                isDragging = true;
                                hasDragged = false;
                                
                                initialX = e.clientX - xOffset;
                                initialY = e.clientY - yOffset;
                                
                                e.preventDefault();
                            });
                            
                            doc.addEventListener('mousemove', (e) => {
                                if (!isDragging) return;
                                hasDragged = true;
                                
                                currentX = e.clientX - initialX;
                                currentY = e.clientY - initialY;
                                
                                xOffset = currentX;
                                yOffset = currentY;

                                container.style.transform = `translate3d(${currentX}px, ${currentY}px, 0)`;
                            });
                            
                            doc.addEventListener('mouseup', () => {
                                if (isDragging) {
                                    isDragging = false;
                                    localStorage.setItem('optibot_x', currentX);
                                    localStorage.setItem('optibot_y', currentY);
                                }
                            });

                            // 3. Intercepter le clic pour empêcher l'ouverture du popover si on a "draggé"
                            btn.addEventListener('click', (e) => {
                                if (hasDragged) {
                                    e.preventDefault();
                                    e.stopPropagation();
                                    hasDragged = false;
                                }
                            }, true);
                        }
                    }
                }
            });
            } catch(e) {
                console.error("Optibot JS Error:", e);
            }
        }
        
        stylePopoverButton();
        setInterval(stylePopoverButton, 500);
        </script>
    """, height=0)
