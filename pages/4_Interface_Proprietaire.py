import streamlit as st
import pandas as pd
from utils.db import load_sql_to_dataframe, execute_query

st.set_page_config(page_title="Interface Propriétaire", page_icon="🏢", layout="wide")

if "user_id" not in st.session_state or st.session_state.get("role") not in ["owner", "admin"]:
    st.warning("Veuillez vous connecter en tant que propriétaire pour accéder à cette page.")
    st.stop()

col1, col2 = st.columns([8, 2])
with col2:
    if st.button("🚪 Se déconnecter", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

st.title("🏢 Espace Propriétaire")
st.markdown("Gérez vos entrepôts et consultez vos contrats en cours.")

owner_id = st.session_state["user_id"]

with st.expander("➕ Déclarer un nouvel entrepôt"):
    with st.form("add_warehouse_form_prop"):
        wh_id = st.text_input("ID Entrepôt (ex: ENT_002)")
        wh_name = st.text_input("Nom de l'entrepôt")
        
        c1, c2, c3 = st.columns(3)
        vol = c1.number_input("Volume (m³)", min_value=1.0, value=1000.0)
        lat = c2.number_input("Latitude", format="%.6f", value=33.5)
        lon = c3.number_input("Longitude", format="%.6f", value=-7.5)
        submit_wh = st.form_submit_button("Ajouter mon entrepôt", type="primary")
        
        if submit_wh:
            if wh_id and wh_name:
                try:
                    execute_query(
                        "INSERT INTO warehouses (warehouse_id, owner_id, name, volume_m3, latitude, longitude, status) VALUES (?, ?, ?, ?, ?, ?, 'available')",
                        (wh_id, owner_id, wh_name, vol, lat, lon)
                    )
                    st.success("Votre entrepôt a été ajouté avec succès !")
                except Exception as e:
                    st.error(f"Erreur : {e}")
            else:
                st.warning("Veuillez renseigner l'ID et le nom.")

st.header("Mes Entrepôts")
df_wh = load_sql_to_dataframe(f"SELECT warehouse_id, name, volume_m3, latitude, longitude, status FROM warehouses WHERE owner_id = {owner_id}")

if not df_wh.empty:
    st.dataframe(df_wh, use_container_width=True, hide_index=True)
    
    with st.expander("📡 Importer un historique IoT (CSV) pour un entrepôt"):
        st.caption("Le fichier CSV doit contenir les colonnes : datetime, T_C1, T_C2, T_C3, H_C1, H_C2, H_C3")
        target_wh = st.selectbox("Sélectionnez l'entrepôt", df_wh['warehouse_id'].tolist())
        uploaded_file = st.file_uploader("Fichier CSV", type=["csv"])
        if uploaded_file is not None:
            if st.button("Importer les données IoT"):
                try:
                    df_iot = pd.read_csv(uploaded_file)
                    # Vérification basique des colonnes
                    req_cols = ['datetime', 'T_C1', 'T_C2', 'T_C3', 'H_C1', 'H_C2', 'H_C3']
                    if all(c in df_iot.columns for c in req_cols):
                        import sqlite3
                        import os
                        DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "optistock.db")
                        conn = sqlite3.connect(DB_PATH)
                        df_insert = pd.DataFrame()
                        df_insert['warehouse_id'] = [target_wh] * len(df_iot)
                        df_insert['recorded_at'] = df_iot['datetime']
                        df_insert['temp_sensor_1'] = df_iot['T_C1']
                        df_insert['temp_sensor_2'] = df_iot['T_C2']
                        df_insert['temp_sensor_3'] = df_iot['T_C3']
                        df_insert['hum_sensor_1'] = df_iot['H_C1']
                        df_insert['hum_sensor_2'] = df_iot['H_C2']
                        df_insert['hum_sensor_3'] = df_iot['H_C3']
                        
                        df_insert.to_sql('iot_readings', conn, if_exists='append', index=False)
                        st.success(f"✅ {len(df_insert)} enregistrements IoT ajoutés avec succès à {target_wh}.")
                    else:
                        st.error(f"Le fichier doit contenir les colonnes : {', '.join(req_cols)}")
                except Exception as e:
                    st.error(f"Erreur lors de l'importation : {e}")
    
    st.subheader("Mes Réservations / Contrats Actifs")
    # Fetch reservations for their warehouses
    warehouse_ids = "', '".join(df_wh['warehouse_id'].tolist())
    query = f"SELECT reservation_id, warehouse_id, status, global_score, created_at FROM reservations WHERE warehouse_id IN ('{warehouse_ids}') AND status IN ('pre_lock', 'confirmed')"
    
    df_res = load_sql_to_dataframe(query)
    if not df_res.empty:
        st.dataframe(df_res, use_container_width=True, hide_index=True)
    else:
        st.info("Aucune réservation active pour le moment.")
else:
    st.warning("Vous ne possédez aucun entrepôt dans le système.")
