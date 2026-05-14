import streamlit as st
import pandas as pd
import sqlite3
import os
from utils.ui import hide_sidebar

# =====================================================
# Configuration de la page
# =====================================================
st.set_page_config(
    page_title="Modifier un Entrepôt - OPTISTOCK SOLUTIONS",
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

if st.session_state.get('user', {}).get('role') != 'owner':
    st.error("🔒 Accès réservé aux propriétaires d'entrepôt.")
    st.stop()
    
# Vérification qu'un entrepôt a bien été sélectionné
wh_id = st.session_state.get("edit_warehouse_id")
if not wh_id:
    st.warning("⚠️ Aucun entrepôt sélectionné pour la modification.")
    st.switch_page("pages/5_Liste_Entrepots.py")
    st.stop()

from core.warehouse_service import get_warehouse_by_id, update_warehouse
wh_data = get_warehouse_by_id(wh_id)

if not wh_data:
    st.error("❌ Entrepôt introuvable.")
    st.stop()

# wh_data est un tuple (name, address, volume_m3, latitude, longitude)
current_name, current_address, current_vol, current_lat, current_lon = wh_data

user_name = st.session_state['user'].get('first_name', 'Propriétaire')

# =====================================================
# CSS léger (équivalent Tailwind)
# =====================================================
st.markdown("""
<style>
body {
    font-family: Inter, sans-serif;
}
.header {
    background: white;
    border-bottom: 1px solid #e1e2e9;
    padding: 16px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.title {
    font-weight: 900;
    font-size: 22px;
    color: #005da7;
}
.section {
    background: white;
    border: 1px solid #e1e2e9;
    border-radius: 16px;
    padding: 24px;
}
.subtitle {
    color: #414751;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# Header
# =====================================================
st.markdown(f"""
<div class="header">
    <div class="title">🏭 OPTISTOCK SOLUTIONS</div>
    <div style="display:flex; gap: 15px; align-items:center;">
        <span style="color: #00457f; font-weight: 600;">👋 Bonjour, {user_name}</span>
        <span>🔔</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.write("")
if st.button("⬅ Retour à la liste", key="back_btn"):
    st.switch_page("pages/5_Liste_Entrepots.py")

st.write("")

# =====================================================
# Titre principal
# =====================================================
st.markdown(f"""
### ⚙️ Modifier l'Entrepôt :{current_name} ({wh_id})
Mettez à jour les paramètres structurels et environnementaux.
""")

st.write("")

# =====================================================
# Layout principal
# =====================================================
left, right = st.columns([8, 4])

# =====================================================
# INFORMATIONS GÉNÉRALES
# =====================================================
with left:
    st.markdown("#### ℹ️ Informations Générales")

    with st.container(border=True):
        nom = st.text_input(
            "Nom de l'entrepôt",
            value=current_name,
            placeholder="Ex : Hub Logistique Nord-Est"
        )

        adresse = st.text_area(
            "Adresse complète (Optionnelle)",
            value=current_address if current_address else "",
            placeholder="Numéro, rue, ville",
            height=90
        )

        gps_col1, gps_col2 = st.columns(2)

        with gps_col1:
            latitude = st.text_input("Latitude", value=str(current_lat), placeholder="48.8566")

        with gps_col2:
            longitude = st.text_input("Longitude", value=str(current_lon), placeholder="2.3522")

    st.write("")

    # =================================================
    # IMPORT ENVIRONNEMENTAL
    # =================================================
    st.markdown("#### 🌡️ Historique environnemental")

    with st.container(border=True):
        fichier_env = st.file_uploader(
            "Fichier CSV des capteurs IoT (Remplacera l'historique existant)",
            type=["csv"]
        )

        if fichier_env:
            df_env = pd.read_csv(fichier_env)
            st.info(f"ℹ️ {len(df_env)} lignes chargées. Ce fichier remplacera l'historique IoT existant après enregistrement.")
            st.dataframe(df_env.head(3))
        else:
            st.markdown("""
<div style="background:#fefce8;border:1px solid #fde68a;border-radius:10px;padding:12px 16px;margin:8px 0;font-size:13px;">
    <strong>📋 Colonnes du fichier CSV attendues</strong><br/>
    <table style="width:100%;margin-top:8px;border-collapse:collapse;">
        <tr style="background:#fef9c3;">
            <th style="padding:5px 8px;text-align:left;">Colonne</th>
            <th style="padding:5px 8px;text-align:left;">Obligatoire</th>
            <th style="padding:5px 8px;text-align:left;">Alias acceptés</th>
        </tr>
        <tr><td style="padding:4px 8px;"><code>date</code></td><td style="padding:4px 8px;">✅ Oui</td><td style="padding:4px 8px;"><code>datetime</code>, <code>timestamp</code>, <code>recorded_at</code>, <code>heure</code>, <code>time</code></td></tr>
        <tr style="background:#fefce8;"><td style="padding:4px 8px;"><code>temp_1</code></td><td style="padding:4px 8px;">✅ Au moins 1</td><td style="padding:4px 8px;"><code>temperature_1</code>, <code>t1</code>, <code>temp1</code></td></tr>
        <tr><td style="padding:4px 8px;"><code>temp_2</code></td><td style="padding:4px 8px;">⚪ Optionnel</td><td style="padding:4px 8px;"><code>temperature_2</code>, <code>t2</code>, <code>temp2</code></td></tr>
        <tr style="background:#fefce8;"><td style="padding:4px 8px;"><code>temp_3</code></td><td style="padding:4px 8px;">⚪ Optionnel</td><td style="padding:4px 8px;"><code>temperature_3</code>, <code>t3</code>, <code>temp3</code></td></tr>
        <tr><td style="padding:4px 8px;"><code>hum_1</code></td><td style="padding:4px 8px;">✅ Au moins 1</td><td style="padding:4px 8px;"><code>humidite_1</code>, <code>humidity_1</code>, <code>h1</code>, <code>hum1</code></td></tr>
        <tr style="background:#fefce8;"><td style="padding:4px 8px;"><code>hum_2</code></td><td style="padding:4px 8px;">⚪ Optionnel</td><td style="padding:4px 8px;"><code>humidite_2</code>, <code>humidity_2</code>, <code>h2</code>, <code>hum2</code></td></tr>
        <tr><td style="padding:4px 8px;"><code>hum_3</code></td><td style="padding:4px 8px;">⚪ Optionnel</td><td style="padding:4px 8px;"><code>humidite_3</code>, <code>humidity_3</code>, <code>h3</code>, <code>hum3</code></td></tr>
    </table>
    <div style="margin-top:10px;background:#fff7ed;border-radius:6px;padding:8px;color:#92400e;font-size:12px;">
        💡 <strong>Exemple minimal :</strong><br/>
        <code>date,temp_1,temp_2,temp_3,hum_1,hum_2,hum_3</code><br/>
        <code>2025-01-01 08:00:00,22.5,21.8,23.1,48.3,47.9,49.0</code>
    </div>
</div>
""", unsafe_allow_html=True)

# =====================================================
# CAPACITÉ & VOLUME
# =====================================================
with right:
    st.markdown("#### 📦 Capacité & Volume")

    with st.container(border=True):
        volume_total = st.number_input(
            "Volume total (m³)",
            value=float(current_vol) if current_vol else 0.0,
            min_value=0.0,
            step=100.0,
            placeholder="50000"
        )

        st.caption("Calculé sur la base de la zone de stockage utile")

# =====================================================
# ACTIONS FINALES
# =====================================================
st.write("")
st.divider()

c1, c2, c3 = st.columns([2, 2, 6])

with c1:
    if st.button("❌ Annuler"):
        st.switch_page("pages/5_Liste_Entrepots.py")

with c2:
    if st.button("💾 Enregistrer les modifications"):
        if not nom or not latitude or not longitude:
            st.error("Veuillez remplir au minimum le nom et les coordonnées GPS.")
        else:
            try:
                lat_val = float(latitude)
                lon_val = float(longitude)
                vol_val = float(volume_total)
                
                success = update_warehouse(wh_id, nom, adresse, vol_val, lat_val, lon_val)
                
                if success:
                    # Importer le CSV IoT si présent
                    if fichier_env is not None:
                        import io
                        fichier_env.seek(0)
                        df_raw = pd.read_csv(io.BytesIO(fichier_env.read()))
                        from core.iot_service import import_iot_csv
                        ok, msg = import_iot_csv(wh_id, df_raw)
                        if ok:
                            st.success(f"✅ Modifications et données IoT enregistrées ! {msg}")
                        else:
                            st.warning(f"⚠️ Modifications enregistrées, mais erreur CSV : {msg}")
                    else:
                        st.success("✅ Modifications enregistrées avec succès !")
                else:
                    st.error("❌ Erreur serveur lors de la mise à jour.")
            except ValueError:
                st.error("Veuillez entrer des valeurs numériques valides pour la latitude et la longitude.")
