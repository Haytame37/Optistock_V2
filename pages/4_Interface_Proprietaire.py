import streamlit as st

# =====================================================
# Configuration de la page
# =====================================================
st.set_page_config(
    page_title="Warehouse Management | LogiTech Admin",
    page_icon="🏭",
    layout="wide"
)

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
st.subheader("Primary Actions")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="action-card">
        <h3 style="color:#00457f;">📦 Gérer les entrepôts existants</h3>
        <p class="small">
        Visualisez, modifiez et surveillez l’état de vos unités de stockage.
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Accéder à la liste ➜", key="manage"):
        st.switch_page("pages/Liste_Entrepots.py")

with col2:
    st.markdown("""
    <div class="action-card">
        <h3 style="color:#9a4600;">➕ Ajouter un nouvel entrepôt</h3>
        <p class="small">
        Enregistrez une nouvelle unité et configurez ses capteurs IoT.
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Démarrer la configuration ➜", key="add"):
        st.switch_page("pages/Ajout_Entrepot.py")

st.write("")

# =====================================================
# Unités récentes (Récupérées de la base de données)
# =====================================================
st.subheader("Unités récentes")

from core.auth import get_recent_warehouses_by_owner
recent_units = get_recent_warehouses_by_owner(st.session_state['user']['user_id'], limit=3)

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
if st.button("Se déconnecter", key="logout_btn"):
    st.session_state.clear()
    st.switch_page("pages/1_Login.py")
# =====================================================
# Footer
# =====================================================
st.write("")
st.caption("LogiTech Admin — Warehouse Monitoring Dashboard")
