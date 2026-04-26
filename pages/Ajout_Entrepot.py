import streamlit as st
import pandas as pd

# =====================================================
# Configuration de la page
# =====================================================
st.set_page_config(
    page_title="Configurer un Entrepôt - OPTISTOCK SOLUTIONS",
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
if st.button("⬅ Retour au tableau de bord", key="back_btn"):
    st.switch_page("pages/4_Interface_Proprietaire.py")

st.write("")

# =====================================================
# Titre principal
# =====================================================
st.markdown("""
### ⚙️ Configurer un Entrepôt
Définissez les paramètres structurels et environnementaux  
pour activer le **monitoring IoT**.
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
            placeholder="Ex : Hub Logistique Nord-Est"
        )

        adresse = st.text_area(
            "Adresse complète",
            placeholder="Numéro, rue, ville",
            height=90
        )

        gps_col1, gps_col2 = st.columns(2)

        with gps_col1:
            latitude = st.text_input("Latitude", placeholder="48.8566")

        with gps_col2:
            longitude = st.text_input("Longitude", placeholder="2.3522")

    st.write("")

    # =================================================
    # IMPORT ENVIRONNEMENTAL
    # =================================================
    st.markdown("#### 🌡️ Historique environnemental (obligatoire)")

    with st.container(border=True):
        fichier_env = st.file_uploader(
            "Importer un fichier CSV (température / humidité)",
            type=["csv"]
        )

        if fichier_env:
            df_env = pd.read_csv(fichier_env)
            st.success("✅ Fichier chargé. Il sera importé en base après enregistrement.")
            st.dataframe(df_env.head())

# =====================================================
# CAPACITÉ & VOLUME
# =====================================================
with right:
    st.markdown("#### 📦 Capacité & Volume")

    with st.container(border=True):
        volume_total = st.number_input(
            "Volume total (m³)",
            min_value=0,
            step=100,
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
        st.switch_page("pages/4_Interface_Proprietaire.py")

with c2:
    if st.button("🚀 Enregistrer & Activer"):
        if not nom or not latitude or not longitude:
            st.error("Veuillez remplir au minimum le nom et les coordonnées GPS.")
        else:
            try:
                lat_val = float(latitude)
                lon_val = float(longitude)
                vol_val = float(volume_total)
                
                from core.auth import add_warehouse
                owner_id = st.session_state['user']['user_id']
                w_id = add_warehouse(owner_id, nom, adresse, vol_val, lat_val, lon_val)
                
                if w_id:
                    # Sauvegarder le CSV en base sinon
                    if fichier_env is not None:
                        import io
                        fichier_env.seek(0)
                        df_raw = pd.read_csv(io.BytesIO(fichier_env.read()))
                        from core.auth import import_iot_csv
                        ok, msg = import_iot_csv(w_id, df_raw)
                        if ok:
                            st.success(f"✅ Entrepôt enregistré ({w_id}) ! {msg}")
                        else:
                            st.warning(f"⚠️ Entrepôt créé ({w_id}), mais erreur CSV : {msg}")
                    else:
                        st.success(f"✅ Entrepôt enregistré en base de données ({w_id}).")
                else:
                    st.error("❌ Erreur serveur lors de l'enregistrement.")
            except ValueError:
                st.error("Veuillez entrer des valeurs numériques valides pour la latitude et la longitude.")
