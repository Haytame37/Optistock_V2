import streamlit as st
import pandas as pd
import os
from core.warehouse_service import get_warehouses_by_owner
from utils.ui import hide_sidebar

# =====================================================
# Configuration de la page
# =====================================================
st.set_page_config(
    page_title="Liste des Entrepôts",
    page_icon="🏬",
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

if st.session_state.get('user', {}).get('role') != 'owner':
    st.error("🔒 Accès réservé aux propriétaires d'entrepôt.")
    st.stop()

user_name = st.session_state['user'].get('first_name', 'Propriétaire')

def on_delete_click(w_id, w_name):
    from core.warehouse_service import delete_warehouse
    if delete_warehouse(w_id):
        st.session_state['delete_toast'] = f"✅ {w_name} supprimé avec succès."
    else:
        st.session_state['delete_toast'] = "❌ Erreur de suppression."

def on_edit_click(w_id):
    st.session_state['redirect_to_edit'] = w_id

if st.session_state.get('redirect_to_edit'):
    w_id = st.session_state['redirect_to_edit']
    del st.session_state['redirect_to_edit']
    st.session_state['edit_warehouse_id'] = w_id
    st.switch_page("pages/7_Modifier_Entrepot.py")

if 'delete_toast' in st.session_state:
    st.toast(st.session_state['delete_toast'])
    del st.session_state['delete_toast']

# =====================================================
# CSS (remplacement Tailwind)
# =====================================================
st.markdown("""
<style>
body {
    font-family: Inter, sans-serif;
}
.header {
    background: #f8f9ff;
    border-bottom: 1px solid #e1e2e9;
    padding: 14px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.card {
    background: white;
    border: 1px solid #e1e2e9;
    border-radius: 16px;
    padding: 20px;
}
.badge-ok {
    background: #dcfce7;
    color: #166534;
    font-size: 10px;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 6px;
}
.badge-unavailable {
    background: #ffedd5;
    color: #9a3412;
    font-size: 10px;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 6px;
}
.badge-maint {
    background: #f1f5f9;
    color: #475569;
    font-size: 10px;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 6px;
}
.small {
    font-size: 13px;
    color: #414751;
}
.title {
    font-weight: 800;
    color: #00457f;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# Top App Bar
# =====================================================
st.markdown(f"""
<div class="header">
    <span class="title">📦</span>
    <span style="color: #00457f; font-weight: 600;">👋 Bonjour, {user_name}</span>
</div>
""", unsafe_allow_html=True)

st.write("")
if st.button("⬅ Retour au tableau de bord", key="back_btn"):
    st.switch_page("pages/4_Interface_Proprietaire.py")

st.write("")

# =====================================================
# Contenu principal (pleine largeur)
# =====================================================
st.title("Liste des Entrepôts")

# -----------------------------
# Recherche & Filtres
# -----------------------------
c1, c2 = st.columns([2, 3])

with c1:
    search = st.text_input("🔎 Rechercher un entrepôt ou une ville")

with c2:
    filtre = st.radio(
        "Statut",
        ["Tous", "Disponible", "Actif", "Non disponible"],
        horizontal=True
    )

st.divider()

real_warehouses = get_warehouses_by_owner(st.session_state['user']['user_id'])

# Uniquement les entrepôts de la base de données
warehouses = real_warehouses

# -----------------------------
# Filtrage
# -----------------------------
if filtre != "Tous":
    warehouses = [w for w in warehouses if w["status"] == filtre]

if search:
    warehouses = [
        w for w in warehouses
        if search.lower() in w["name"].lower()
        or search.lower() in w["address"].lower()
    ]

# -----------------------------
# Grille des entrepôts
# -----------------------------
if len(warehouses) == 0:
    st.info("Aucun entrepôt trouvé avec ces critères.")
else:
    cols = st.columns(3)
    
    for idx, wh in enumerate(warehouses):
        with cols[idx % 3]:
            badge_class = {
                "Disponible": "badge-ok",
                "Non disponible": "badge-unavailable",
                "Actif": "badge-ok"
            }.get(wh["status"], "badge-ok")
    
            st.markdown(f"""
            <div class="card">
                <span class="{badge_class}" style="{'background:#dbeafe; color:#1e40af;' if wh['status'] == 'Actif' else ''}">{wh["status"].upper()}</span>
                <h4 style="margin-top:8px;">{wh["name"]}</h4>
                <p class="small">📍 {wh["address"]}</p>
                <p class="small">🛰 GPS: {wh["gps"]}</p>
            </div>
            """, unsafe_allow_html=True)
    
            c_edit, c_del, c_iot = st.columns([1, 1, 1])
            c_edit.button("✏️ Modif", key=f"edit_{wh['id']}", on_click=on_edit_click, args=(wh["id"],))
            c_del.button("🗑 Suppr", key=f"del_{wh['id']}", on_click=on_delete_click, args=(wh["id"], wh["name"]))
            
            if c_iot.button("📊 IoT", key=f"iot_{wh['id']}", type="primary"):
                st.switch_page("pages/8_Dashboard_IoT.py")

# -----------------------------
# Bouton Ajouter
# -----------------------------
st.write("")
if st.button("➕ Ajouter un entrepôt"):
    st.switch_page("pages/6_Ajout_Entrepot.py")
