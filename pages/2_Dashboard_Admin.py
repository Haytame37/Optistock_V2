import streamlit as st
import bcrypt
import uuid
from utils.db import load_sql_to_dataframe, execute_query
from models.reservation import Reservation

st.set_page_config(page_title="Dashboard Admin", page_icon="⚙️", layout="wide")

if "user_id" not in st.session_state or st.session_state.get("role") != "admin":
    st.warning("Veuillez vous connecter en tant qu'administrateur pour accéder à cette page.")
    st.stop()

col1, col2 = st.columns([8, 2])
with col2:
    if st.button("🚪 Se déconnecter", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

st.sidebar.title("⚙️ Administration")
admin_view = st.sidebar.radio("Gestion", [
    "👥 Utilisateurs", 
    "🏢 Entrepôts", 
    "🎯 Points de Livraison", 
    "📝 Réservations"
])

def render_users_page():
    st.title("👥 Gestion des Utilisateurs")
    st.caption("Visualisez et ajoutez de nouveaux utilisateurs.")
    
    with st.expander("➕ Ajouter un nouvel utilisateur"):
        with st.form("add_user_form"):
            c1, c2 = st.columns(2)
            first_name = c1.text_input("Prénom")
            last_name = c2.text_input("Nom")
            email = st.text_input("Email")
            password = st.text_input("Mot de passe", type="password")
            role = st.selectbox("Rôle", ["admin", "owner", "researcher"])
            submit_user = st.form_submit_button("Créer l'utilisateur", type="primary")
            
            if submit_user:
                if first_name and last_name and email and password:
                    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    try:
                        execute_query(
                            f"INSERT INTO users (role, first_name, last_name, email, password_hash) VALUES (?, ?, ?, ?, ?)",
                            (role, first_name, last_name, email, hashed_pw)
                        )
                        st.success("Utilisateur créé avec succès ! Veuillez rafraîchir la page.")
                    except Exception as e:
                        st.error(f"Erreur lors de la création : {e}")
                else:
                    st.warning("Veuillez remplir tous les champs.")

    st.subheader("Liste des Utilisateurs")
    df_users = load_sql_to_dataframe("SELECT user_id, role, first_name, last_name, email, is_active, created_at FROM users")
    if not df_users.empty:
        st.dataframe(df_users, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.markdown("### 🛠️ Actions sur les comptes")
        with st.form("user_actions_form"):
            user_to_mod = st.selectbox("Sélectionnez l'utilisateur :", df_users['email'].tolist())
            action = st.radio("Action à effectuer :", ["Désactiver le compte", "Réactiver le compte", "Supprimer le compte (Irréversible)"])
            submit_action = st.form_submit_button("Appliquer l'action", type="primary")
            
            if submit_action:
                if user_to_mod:
                    target_id = df_users.loc[df_users['email'] == user_to_mod, 'user_id'].values[0]
                    # Prevent admin from deleting themselves
                    if target_id == st.session_state.get("user_id"):
                        st.error("❌ Vous ne pouvez pas modifier ou supprimer votre propre compte admin actuel.")
                    else:
                        try:
                            if "Désactiver" in action:
                                execute_query(f"UPDATE users SET is_active = 0 WHERE user_id = {target_id}")
                                st.success(f"✅ Compte {user_to_mod} désactivé avec succès.")
                            elif "Réactiver" in action:
                                execute_query(f"UPDATE users SET is_active = 1 WHERE user_id = {target_id}")
                                st.success(f"✅ Compte {user_to_mod} réactivé avec succès.")
                            elif "Supprimer" in action:
                                execute_query(f"DELETE FROM users WHERE user_id = {target_id}")
                                st.warning(f"⚠️ Compte {user_to_mod} supprimé de la base de données.")
                            
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erreur lors de l'exécution de l'action : {e}")
    else:
        st.info("Aucun utilisateur trouvé.")

def render_warehouses_page():
    st.title("🏢 Catalogue des Entrepôts")
    st.caption("Vue d'ensemble et ajout de nouveaux entrepôts.")
    
    with st.expander("➕ Ajouter un nouvel entrepôt"):
        with st.form("add_warehouse_form"):
            wh_id = st.text_input("ID Entrepôt (ex: ENT_002)")
            wh_name = st.text_input("Nom de l'entrepôt")
            
            # Charger les propriétaires pour la liste déroulante
            df_owners = load_sql_to_dataframe("SELECT user_id, email FROM users WHERE role = 'owner'")
            owner_options = dict(zip(df_owners['email'], df_owners['user_id'])) if not df_owners.empty else {"Aucun (Erreur)": 1}
            owner_email = st.selectbox("Propriétaire", list(owner_options.keys()))
            
            c1, c2, c3 = st.columns(3)
            vol = c1.number_input("Volume (m³)", min_value=1.0, value=1000.0)
            lat = c2.number_input("Latitude", format="%.6f", value=33.5)
            lon = c3.number_input("Longitude", format="%.6f", value=-7.5)
            submit_wh = st.form_submit_button("Ajouter l'entrepôt", type="primary")
            
            if submit_wh:
                if wh_id and wh_name:
                    owner_id = owner_options[owner_email]
                    try:
                        execute_query(
                            "INSERT INTO warehouses (warehouse_id, owner_id, name, volume_m3, latitude, longitude, status) VALUES (?, ?, ?, ?, ?, ?, 'available')",
                            (wh_id, owner_id, wh_name, vol, lat, lon)
                        )
                        st.success("Entrepôt ajouté avec succès !")
                    except Exception as e:
                        st.error(f"Erreur : {e}")
                else:
                    st.warning("Veuillez renseigner l'ID et le nom.")

    st.subheader("Liste des Entrepôts")
    df_wh = load_sql_to_dataframe("SELECT warehouse_id, owner_id, name, volume_m3, latitude, longitude, status, updated_at FROM warehouses")
    
    if not df_wh.empty:
        if "latitude" in df_wh.columns and "longitude" in df_wh.columns:
            st.map(df_wh[["latitude", "longitude"]])
        st.dataframe(df_wh, use_container_width=True, hide_index=True)
    else:
        st.info("Aucun entrepôt trouvé dans le catalogue.")

def render_delivery_points_page():
    st.title("🎯 Points de Livraison")
    st.caption("Gérez les points de demande de livraison des chercheurs.")
    
    with st.expander("➕ Déclarer un point de livraison"):
        with st.form("add_dp_form"):
            dp_name = st.text_input("Nom de la demande (Projet)")
            dp_type = st.selectbox("Type de produit", ["froid", "sec", "dangereux", "mixte"])
            
            # Charger les chercheurs
            df_res = load_sql_to_dataframe("SELECT user_id, email FROM users WHERE role = 'researcher'")
            res_options = dict(zip(df_res['email'], df_res['user_id'])) if not df_res.empty else {"Aucun": 1}
            res_email = st.selectbox("Chercheur assigné", list(res_options.keys()))
            
            c1, c2 = st.columns(2)
            lat = c1.number_input("Latitude ciblée", format="%.6f", value=33.5)
            lon = c2.number_input("Longitude ciblée", format="%.6f", value=-7.5)
            submit_dp = st.form_submit_button("Créer le point de livraison", type="primary")
            
            if submit_dp:
                if dp_name:
                    req_id = "REQ_" + str(uuid.uuid4())[:8]
                    researcher_id = res_options[res_email]
                    try:
                        execute_query(
                            "INSERT INTO delivery_points (request_id, researcher_id, name, product_type, latitude, longitude) VALUES (?, ?, ?, ?, ?, ?)",
                            (req_id, researcher_id, dp_name, dp_type, lat, lon)
                        )
                        st.success("Point de livraison ajouté !")
                    except Exception as e:
                        st.error(f"Erreur : {e}")
                else:
                    st.warning("Veuillez renseigner un nom.")
                    
    st.subheader("Carte des Points de Livraison")
    df_dp = load_sql_to_dataframe("SELECT request_id, researcher_id, name, product_type, latitude, longitude FROM delivery_points")
    if not df_dp.empty:
        st.map(df_dp[["latitude", "longitude"]])
        st.dataframe(df_dp, use_container_width=True, hide_index=True)
    else:
        st.info("Aucun point de livraison actuellement enregistré.")

def render_reservations_page():
    st.title("📝 Suivi des Réservations")
    st.caption("Gérez le cycle de vie complet des réservations.")
    
    Reservation._purger_verrous_expires_cls()
    
    df_res = load_sql_to_dataframe("SELECT reservation_id, warehouse_id, researcher_id, status, global_score, reason, created_at, expires_at FROM reservations ORDER BY created_at DESC")
    if not df_res.empty:
        st.dataframe(df_res, use_container_width=True, hide_index=True)
    else:
        st.info("Aucune réservation trouvée.")
        
    st.divider()
    st.subheader("⚙️ Actions Administratives")
    col1, col2 = st.columns(2)
    with col1:
        res_id = st.text_input("ID Réservation à modifier")
        action = st.selectbox("Nouvelle Action", ["Confirmer", "Annuler"])
    with col2:
        st.write("")
        st.write("")
        if st.button("Appliquer la modification", type="primary"):
            if res_id:
                new_status = "confirmed" if action == "Confirmer" else "canceled"
                execute_query(f"UPDATE reservations SET status = '{new_status}', reason = 'Action administrative' WHERE reservation_id = '{res_id}'")
                
                df_target = load_sql_to_dataframe(f"SELECT warehouse_id FROM reservations WHERE reservation_id = '{res_id}'")
                if not df_target.empty:
                    w_id = df_target.iloc[0]["warehouse_id"]
                    if new_status == "confirmed":
                        execute_query(f"UPDATE warehouses SET status = 'unavailable' WHERE warehouse_id = '{w_id}'")
                    else:
                        execute_query(f"UPDATE warehouses SET status = 'available' WHERE warehouse_id = '{w_id}'")
                
                st.success(f"La réservation {res_id} a été mise à jour vers '{new_status}'.")
                st.rerun()
            else:
                st.error("Veuillez saisir un ID de réservation.")

if admin_view == "👥 Utilisateurs":
    render_users_page()
elif admin_view == "🏢 Entrepôts":
    render_warehouses_page()
elif admin_view == "🎯 Points de Livraison":
    render_delivery_points_page()
elif admin_view == "📝 Réservations":
    render_reservations_page()
