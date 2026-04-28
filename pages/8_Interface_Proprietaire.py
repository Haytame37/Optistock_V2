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
        st.switch_page("pages/5_Liste_Entrepots.py")

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
        st.switch_page("pages/6_Ajout_Entrepot.py")

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


st.divider()

# =====================================================
# Import CSV données IoT capteurs
# =====================================================
st.subheader("📡 Import de données IoT (Capteurs)")

owner_id   = st.session_state['user']['user_id']
from core.auth import get_warehouses_by_owner
my_wh = get_warehouses_by_owner(owner_id)

if not my_wh:
    st.info("Aucun entrepôt enregistré. Ajoutez un entrepôt pour pouvoir importer des données IoT.")
else:
    wh_options = {w['name']: w['id'] for w in my_wh}
    selected_wh_name = st.selectbox("Sélectionnez l'entrepôt cible", list(wh_options.keys()), key="iot_wh_select")
    selected_wh_id   = wh_options[selected_wh_name]

    iot_file = st.file_uploader(
        "Fichier CSV des capteurs IoT",
        type=["csv"],
        key="iot_upload",
        label_visibility="collapsed"
    )

    if iot_file:
        import pandas as pd
        df_preview = pd.read_csv(iot_file)
        st.success(f"✅ {len(df_preview)} lignes chargées — Aperçu :")
        st.dataframe(df_preview.head(3))

        if st.button("💾 Importer dans la base de données", key="iot_import_btn", type="primary"):
            iot_file.seek(0)
            from core.auth import import_iot_csv
            ok, msg = import_iot_csv(selected_wh_id, pd.read_csv(iot_file))
            if ok:
                st.success(msg)
            else:
                st.error(msg)
    else:
        st.markdown("""
<div style="background:#fefce8;border:1px solid #fde68a;border-radius:10px;padding:12px 16px;margin:8px 0;font-size:13px;">
    <strong>📋 Colonnes requises</strong><br/>
    <table style="width:100%;margin-top:8px;border-collapse:collapse;">
        <tr style="background:#fef9c3;">
            <th style="padding:5px 8px;text-align:left;">Colonne</th>
            <th style="padding:5px 8px;text-align:left;">Obligatoire</th>
            <th style="padding:5px 8px;text-align:left;">Alias acceptés</th>
        </tr>
        <tr><td style="padding:4px 8px;"><code>date</code></td><td style="padding:4px 8px;">✅ Oui</td><td style="padding:4px 8px;"><code>datetime</code>, <code>timestamp</code>, <code>recorded_at</code>, <code>heure</code></td></tr>
        <tr style="background:#fefce8;"><td style="padding:4px 8px;"><code>temp_1</code></td><td style="padding:4px 8px;">✅ Au moins 1</td><td style="padding:4px 8px;"><code>temperature_1</code>, <code>t1</code>, <code>temp1</code></td></tr>
        <tr><td style="padding:4px 8px;"><code>temp_2</code></td><td style="padding:4px 8px;">⚪ Optionnel</td><td style="padding:4px 8px;"><code>temperature_2</code>, <code>t2</code>, <code>temp2</code></td></tr>
        <tr style="background:#fefce8;"><td style="padding:4px 8px;"><code>temp_3</code></td><td style="padding:4px 8px;">⚪ Optionnel</td><td style="padding:4px 8px;"><code>temperature_3</code>, <code>t3</code>, <code>temp3</code></td></tr>
        <tr><td style="padding:4px 8px;"><code>hum_1</code></td><td style="padding:4px 8px;">✅ Au moins 1</td><td style="padding:4px 8px;"><code>humidite_1</code>, <code>humidity_1</code>, <code>h1</code></td></tr>
        <tr style="background:#fefce8;"><td style="padding:4px 8px;"><code>hum_2</code></td><td style="padding:4px 8px;">⚪ Optionnel</td><td style="padding:4px 8px;"><code>humidite_2</code>, <code>humidity_2</code>, <code>h2</code></td></tr>
        <tr><td style="padding:4px 8px;"><code>hum_3</code></td><td style="padding:4px 8px;">⚪ Optionnel</td><td style="padding:4px 8px;"><code>humidite_3</code>, <code>humidity_3</code>, <code>h3</code></td></tr>
    </table>
    <div style="margin-top:8px;color:#92400e;font-size:12px;">💡 Exemple minimal : <code>date,temp_1,hum_1</code><br/>2025-01-01 08:00:00,22.5,48.3</div>
</div>
""", unsafe_allow_html=True)

if st.button("Se déconnecter", key="logout_btn"):
    st.session_state.clear()
    st.switch_page("pages/1_Login.py")
st.write("")
st.caption("LogiTech Admin — Warehouse Monitoring Dashboard")
