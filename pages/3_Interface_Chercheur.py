import streamlit as st
import pandas as pd
from utils.product_conditions import PRODUCT_CONDITIONS
from core.iot_filter import get_compliant_warehouses

# =====================================================
# Vérification de sécurité (Indispensable)
# =====================================================
if 'logged_in' not in st.session_state or not st.session_state.get('logged_in'):
    st.warning("🔒 Accès refusé. Veuillez vous connecter d'abord.")
    st.switch_page("pages/1_Login.py")
    st.stop()

if st.session_state.get('role') not in ["researcher", "admin"]:
    st.error("🔒 Accès réservé aux chercheurs ou administrateurs.")
    st.stop()

# =====================================================
# Configuration de la page
# =====================================================
st.set_page_config(
    page_title="OPTISTOCK Solutions",
    page_icon="📦",
    layout="wide"
)

# =====================================================
# CSS personnalisé (équivalent Tailwind simplifié)
# =====================================================
st.markdown("""
<style>
body {
    font-family: Inter, sans-serif;
}
.header {
    padding: 16px 24px;
    background-color: #f4fafd;
    border-bottom: 1px solid rgba(0,93,167,0.15);
}
.brand {
    color: #005da7;
    font-weight: 900;
    letter-spacing: -0.8px;
}
.subtitle {
    color: #414751;
    max-width: 700px;
}
.card {
    background: white;
    border: 1px solid #e1e2e9;
    border-radius: 14px;
    padding: 24px;
    height: 100%;
}
.upload-box {
    border: 2px dashed rgba(0,69,127,0.3);
    border-radius: 16px;
    padding: 24px;
    background: rgba(0,69,127,0.05);
}
.label {
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    color: #00457f;
}
.hint {
    font-size: 13px;
    color: #727782;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# Header
# =====================================================
st.markdown("""
<div class="header">
    <h2 class="brand">📦 OPTISTOCK Solutions</h2>
</div>
""", unsafe_allow_html=True)

st.write("")

# =====================================================
# Titre principal
# =====================================================
st.markdown("""
<h1 style="color:#00457f">Nouveau Dispatch Logistique</h1>
<p class="subtitle">
Configurez votre demande de transport et importez les données de destination
pour initialiser le moteur d'optimisation.
</p>
""", unsafe_allow_html=True)

st.write("")

# =====================================================
# Layout principal
# =====================================================
left, right = st.columns([4, 8])

# =====================================================
# COLONNE GAUCHE — IMPORT DES DONNÉES
# =====================================================
with left:
    st.markdown("""
    <div class="card">
        <h3>📤 Import de données</h3>
    """, unsafe_allow_html=True)

    st.markdown('<p class="label">Import des points de livraison</p>', unsafe_allow_html=True)
    livraison_file = st.file_uploader(
        "CSV des points de livraison",
        type=["csv"],
        key="livraisons",
        label_visibility="collapsed"
    )

    if livraison_file:
        df_livraison = pd.read_csv(livraison_file)
        st.success(f"✅ {len(df_livraison)} points de livraison importés")
        st.dataframe(df_livraison.head(3))
    else:
        st.markdown("""
<div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;padding:12px 16px;margin:8px 0;font-size:13px;">
    <strong>📋 Colonnes requises</strong><br/>
    <table style="width:100%;margin-top:8px;border-collapse:collapse;">
        <tr style="background:#dbeafe;">
            <th style="padding:5px 8px;text-align:left;">Colonne</th>
            <th style="padding:5px 8px;text-align:left;">Obligatoire</th>
            <th style="padding:5px 8px;text-align:left;">Alias acceptés</th>
        </tr>
        <tr><td style="padding:4px 8px;"><code>name</code></td><td style="padding:4px 8px;">✅ Oui</td><td style="padding:4px 8px;"><code>nom</code>, <code>point</code></td></tr>
        <tr style="background:#f0f9ff;"><td style="padding:4px 8px;"><code>latitude</code></td><td style="padding:4px 8px;">✅ Oui</td><td style="padding:4px 8px;"><code>lat</code></td></tr>
        <tr><td style="padding:4px 8px;"><code>longitude</code></td><td style="padding:4px 8px;">✅ Oui</td><td style="padding:4px 8px;"><code>lon</code></td></tr>
    </table>
    <div style="margin-top:8px;color:#1d4ed8;font-size:12px;">💡 Exemple : <code>name,latitude,longitude</code><br/>Paris Centre,48.8566,2.3522</div>
</div>
""", unsafe_allow_html=True)

    st.write("")

    st.markdown('<p class="label">Import des entrepôts existants</p>', unsafe_allow_html=True)
    entrepot_file = st.file_uploader(
        "CSV des entrepôts",
        type=["csv"],
        key="entrepots",
        label_visibility="collapsed"
    )

    if entrepot_file:
        df_entrepot = pd.read_csv(entrepot_file)
        st.success(f"✅ {len(df_entrepot)} entrepôts importés")
        st.dataframe(df_entrepot.head(3))
    else:
        st.markdown("""
<div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;padding:12px 16px;margin:8px 0;font-size:13px;">
    <strong>📋 Colonnes requises</strong><br/>
    <table style="width:100%;margin-top:8px;border-collapse:collapse;">
        <tr style="background:#dcfce7;">
            <th style="padding:5px 8px;text-align:left;">Colonne</th>
            <th style="padding:5px 8px;text-align:left;">Obligatoire</th>
            <th style="padding:5px 8px;text-align:left;">Alias acceptés</th>
        </tr>
        <tr><td style="padding:4px 8px;"><code>id_entrepot</code></td><td style="padding:4px 8px;">✅ Oui</td><td style="padding:4px 8px;"><code>id</code></td></tr>
        <tr style="background:#f0fdf4;"><td style="padding:4px 8px;"><code>nom</code></td><td style="padding:4px 8px;">⚪ Non</td><td style="padding:4px 8px;"><code>name</code>, <code>entrepot</code></td></tr>
        <tr><td style="padding:4px 8px;"><code>adresse</code></td><td style="padding:4px 8px;">⚪ Non</td><td style="padding:4px 8px;"><code>address</code></td></tr>
        <tr style="background:#f0fdf4;"><td style="padding:4px 8px;"><code>latitude</code></td><td style="padding:4px 8px;">✅ Oui</td><td style="padding:4px 8px;"><code>lat</code></td></tr>
        <tr><td style="padding:4px 8px;"><code>longitude</code></td><td style="padding:4px 8px;">✅ Oui</td><td style="padding:4px 8px;"><code>lon</code></td></tr>
    </table>
    <div style="margin-top:8px;color:#15803d;font-size:12px;">💡 Exemple : <code>id_entrepot,nom,adresse,latitude,longitude</code><br/>ENT001,Entrepôt Casablanca,Av. Hassan II,33.5731,-7.5898</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# COLONNE DROITE — FORMULAIRE
# =====================================================
with right:
    with st.form("optimisation_form"):
        st.markdown("""
        <div class="card">
            <h3>⚙️ Paramètres de la demande</h3>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)

        with c1:
            produit = st.selectbox(
                "Type de produit",
                options=list(PRODUCT_CONDITIONS.keys())
            )

        with c2:
            volume = st.number_input(
                "Volume total (m³)",
                min_value=0.0,
                step=0.1,
                placeholder="3"
            )

        duree = st.number_input(
            "Durée de stockage estimée (jours)",
            min_value=1,
            max_value=365,
            placeholder="7"
        )


        submit = st.form_submit_button("🚀 Lancer l’optimisation")

        st.markdown("</div>", unsafe_allow_html=True)

        if submit:
            import uuid
            import sqlite3
            from utils.db import DB_PATH

            researcher_id = st.session_state.get("user_id")
            
            # Sauvegarder les points de livraison
            saved_points = 0
            if livraison_file is not None:
                try:
                    livraison_file.seek(0)
                    df_livraison = pd.read_csv(livraison_file)
                    
                    if not df_livraison.empty:
                        # Nettoyage des noms de colonnes
                        df_livraison.columns = [c.strip().lower() for c in df_livraison.columns]
                        
                        conn = sqlite3.connect(DB_PATH)
                        cursor = conn.cursor()
                        for _, row in df_livraison.iterrows():
                            # Mapping flexible
                            name = row.get('name', row.get('nom', row.get('point', 'Point Inconnu')))
                            lat = row.get('latitude', row.get('lat', 0.0))
                            lon = row.get('longitude', row.get('lon', 0.0))
                            
                            req_id = str(uuid.uuid4())[:8]
                            cursor.execute("""
                                INSERT INTO delivery_points (request_id, researcher_id, name, latitude, longitude)
                                VALUES (?, ?, ?, ?, ?)
                            """, (req_id, researcher_id, name, lat, lon))
                            saved_points += 1
                        conn.commit()
                        conn.close()
                except Exception as e:
                    st.error(f"❌ Erreur points de livraison : {e}")

            # Sauvegarder les entrepôts
            saved_warehouses = 0
            if entrepot_file is not None:
                try:
                    entrepot_file.seek(0)
                    df_entrepot = pd.read_csv(entrepot_file)
                    
                    if not df_entrepot.empty:
                        # Nettoyage des noms de colonnes
                        df_entrepot.columns = [c.strip().lower() for c in df_entrepot.columns]

                        conn = sqlite3.connect(DB_PATH)
                        cursor = conn.cursor()
                        for _, row in df_entrepot.iterrows():
                            # Mapping flexible
                            w_id = row.get('id_entrepot', row.get('id', str(uuid.uuid4())[:8]))
                            w_nom = row.get('name', row.get('nom', row.get('entrepot', 'Entrepôt Importé')))
                            w_adr = row.get('adresse', row.get('address', 'Inconnue'))
                            w_lat = row.get('latitude', row.get('lat', 0.0))
                            w_lon = row.get('longitude', row.get('lon', 0.0))
                            
                            cursor.execute("""
                                INSERT OR REPLACE INTO my_warehouse (id_entrepot, researcher_id, nom, adresse, latitude, longitude)
                                VALUES (?, ?, ?, ?, ?, ?)
                            """, (w_id, researcher_id, w_nom, w_adr, w_lat, w_lon))
                            saved_warehouses += 1
                        conn.commit()
                        conn.close()
                except Exception as e:
                    st.error(f"❌ Erreur entrepôts : {e}")

            st.success(f"✅ Optimisation lancée ! {saved_points} points et {saved_warehouses} entrepôts enregistrés.")
            })

            # --- NOUVELLE SECTION : PROPOSITIONS D'ENTREPÔTS ---
            st.markdown("---")
            st.markdown("### 🏘️ Entrepôts suggérés (Conformité IoT)")
            
            with st.spinner("Analyse des historiques IoT en cours..."):
                suggestions = get_compliant_warehouses(produit, researcher_id=researcher_id)
            
            if suggestions:
                st.info(f"Basé sur les conditions de conservation pour **{produit}**, voici les entrepôts conformes détectés dans notre réseau :")
                
                # Transformer en DataFrame pour l'affichage
                df_sugg = pd.DataFrame(suggestions)
                
                # Mise en forme
                st.dataframe(
                    df_sugg[["nom", "avg_temp", "avg_hum", "status"]],
                    column_config={
                        "nom": "Nom de l'entrepôt",
                        "avg_temp": st.column_config.NumberColumn("T° Moyenne (Recent)", format="%.1f °C"),
                        "avg_hum": st.column_config.NumberColumn("Humidité Moyenne", format="%.1f %%"),
                        "status": "Statut"
                    },
                    use_container_width=True,
                    hide_index=True
                )
                
                # Bouton pour utiliser ces entrepôts (Simulé pour l'instant)
                st.success(f"✅ {len(suggestions)} entrepôts sont prêts pour le traitement logistique.")
            else:
                st.warning(f"⚠️ Aucun entrepôt actuellement en service ne respecte strictement les conditions pour **{produit}**.")

# Bouton de déconnexion (Optionnel mais recommandé)
st.write("")
if st.button("🚪 Se déconnecter"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.switch_page("pages/1_Login.py")