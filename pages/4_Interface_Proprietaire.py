import pandas as pd
import streamlit as st

from core.messaging import (
    REQUEST_ACCEPTED,
    REQUEST_PENDING,
    ensure_messaging_schema,
    get_chat_messages,
    get_owner_requests,
    send_chat_message,
    update_contact_request_status,
)
from utils.ui import hide_sidebar

# =====================================================
# Configuration de la page
# =====================================================
st.set_page_config(
    page_title="Warehouse Management | LogiTech Admin",
    page_icon="🏭",
    layout="wide"
)
hide_sidebar()

# =====================================================
# Vérification de sécurité
# =====================================================
if 'logged_in' not in st.session_state or not st.session_state.get('logged_in'):
    st.warning("🔒 Accès refusé. Veuillez vous connecter d'abord.")
    st.switch_page("pages/1_Login.py")
    st.stop()

if st.session_state.get('role') != 'owner' and st.session_state.get('user', {}).get('role') != 'owner':
    st.error("🔒 Accès réservé aux propriétaires d'entrepôt.")
    st.stop()

ensure_messaging_schema()
owner_id = st.session_state.get('user_id') or st.session_state.get('user', {}).get('user_id')
user_name = (
    st.session_state.get('user', {}).get('first_name')
    or st.session_state.get('first_name')
    or 'Propriétaire'
)

# =====================================================
# CSS (style simplifié)
# =====================================================
st.markdown("""
<style>
body {
    font-family: Inter, sans-serif;
}
.header {
    background-color: #f8f9ff;
    padding: 16px 24px;
    border-bottom: 1px solid #c1c7d3;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.app-title {
    font-size: 22px;
    font-weight: 700;
    color: #00457f;
}
.card {
    background: white;
    border: 1px solid #c1c7d3;
    border-radius: 14px;
    padding: 24px;
}
.action-card {
    border-radius: 16px;
    border: 1px solid #c1c7d3;
    padding: 24px;
}
.small {
    font-size: 13px;
    color: #414751;
}

.badge-ok {
    background: #dcfce7;
    color: #166534;
    font-size: 10px;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 6px;
}
.badge-unavailable {
    background: #ffedd5;
    color: #9a3412;
    font-size: 10px;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 6px;
}
.badge-maint {
    background: #f1f5f9;
    color: #475569;
    font-size: 10px;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 6px;
}
.status-text {
    font-weight: 700;
    font-size: 13px;
}
.status-ok {
    color: #166534;
}
.status-unavailable {
    color: #9a3412;
}
.status-maint {
    color: #475569;
}
.chat-bubble {
    border: 1px solid #dbe4ee;
    border-radius: 14px;
    padding: 12px 14px;
    margin-bottom: 10px;
    background: #f8fbff;
}
.chat-meta {
    font-size: 12px;
    color: #64748b;
    margin-bottom: 6px;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# Header
# =====================================================
st.markdown(f"""
<div class="header">
    <span class="app-title">🏭 </span>
    <span style="color: #00457f; font-weight: 600;">👋 Bonjour, {user_name}</span>
</div>
""", unsafe_allow_html=True)


st.write("")

# =====================================================
# Actions principales
# =====================================================
st.subheader("Actions principales")

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.markdown('<h3 style="color:#00457f; margin-top:0;">📦 Gérer les entrepôts</h3>', unsafe_allow_html=True)
        st.markdown('<p style="font-size:13px; color:#414751;">Visualisez, modifiez et surveillez l’état de vos unités de stockage.</p>', unsafe_allow_html=True)
        if st.button("Accéder à la liste ➜", key="manage", use_container_width=True):
            st.switch_page("pages/5_Liste_Entrepots.py")

with col2:
    with st.container(border=True):
        st.markdown('<h3 style="color:#9a4600; margin-top:0;">➕ Ajouter un entrepôt</h3>', unsafe_allow_html=True)
        st.markdown('<p style="font-size:13px; color:#414751;">Enregistrez une nouvelle unité et configurez ses capteurs IoT.</p>', unsafe_allow_html=True)
        if st.button("Démarrer la configuration ➜", key="add", use_container_width=True):
            st.switch_page("pages/6_Ajout_Entrepot.py")

with col3:
    try:
        _pq = get_owner_requests(owner_id)
        _pending_n = len(_pq[_pq["status"] == REQUEST_PENDING]) if not _pq.empty else 0
    except Exception:
        _pending_n = 0
    _badge = (
        f'<span style="background:#ef4444;color:#fff;border-radius:999px;'
        f'padding:1px 8px;font-size:11px;font-weight:700;">{_pending_n}</span>'
        if _pending_n > 0 else ""
    )
    with st.container(border=True):
        st.markdown(f'<h3 style="color:#1d4ed8; margin-top:0;">💬 Messagerie {_badge}</h3>', unsafe_allow_html=True)
        st.markdown('<p style="font-size:13px; color:#414751;">Gérez les demandes des chercheurs et échangez en temps réel avec eux.</p>', unsafe_allow_html=True)
        if st.button("💬 Ouvrir la messagerie ➜", key="goto_msg", use_container_width=True, type="primary"):
            st.switch_page("pages/11_Messagerie_Proprietaire.py")

st.write("")

# =====================================================
# Unités récentes (Récupérées de la base de données)
# =====================================================
st.subheader("Unités récentes")

from core.warehouse_service import get_recent_warehouses_by_owner
recent_units = get_recent_warehouses_by_owner(owner_id, limit=3)

if not recent_units:
    st.info("Aucun entrepôt enregistré pour le moment.")
else:
    for unit in recent_units:
        badge_class = "badge-ok"
        if unit['status'] == "Non disponible": badge_class = "badge-unavailable"
        elif unit['status'] == "Maintenance": badge_class = "badge-maint"
        
        st.markdown(f"""
        <div class="card" style="margin-bottom: 16px;">
            <div style="display:flex; justify-content: space-between; align-items:center;">
                <div>
                    <span class="{badge_class}">{unit['status']}</span>
                    <h4>{unit['name']}</h4>
                </div>
                <span class="status-text {"status-ok" if unit['status']=="Disponible" else "status-unavailable" if unit['status']=="Non disponible" else "status-maint"}">{unit['status']}</span>
            </div>
            <p class="small">📍 {unit['address']}</p>
            <p class="small">🛰 GPS: {unit['gps']}</p>
        </div>
        """, unsafe_allow_html=True)

st.write("")
if st.button("🚪 Se déconnecter", key="logout_btn"):
    st.session_state.clear()
    st.switch_page("app.py")
st.write("")
st.caption("OptiStock — Warehouse Monitoring Dashboard")
