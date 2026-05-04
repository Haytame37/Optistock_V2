import streamlit as st
import uuid
import pandas as pd
from utils.db import load_sql_to_dataframe, execute_query, get_db_connection
from models.reservation import Reservation
from core.auth import hash_password
from utils.helpers import get_current_time
from utils.ui import hide_sidebar

# =====================================================
# Configuration de la page
# =====================================================
st.set_page_config(
    page_title="OptiStock – Administration",
    page_icon="⚙️",
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

if st.session_state.get('role') != "admin":
    st.error(f"🔒 Accès réservé aux administrateurs. Votre rôle : {st.session_state.get('role')}")
    st.stop()

# =====================================================
# CSS Personnalisé (Premium Design)
# =====================================================
st.markdown("""
<style>
    html, body, [class*="css"] {
        font-family: sans-serif;
    }
    
    .main {
        background-color: #f8fafc;
    }
    
    .stCard {
        background: white;
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    
    .kpi-card {
        background: linear-gradient(135deg, #005da7 0%, #003d6e 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
    }
    
    .kpi-value {
        font-size: 2rem;
        font-weight: 800;
    }
    
    .kpi-label {
        font-size: 0.9rem;
        opacity: 0.8;
    }
    
    .section-title {
        color: #1e293b;
        font-weight: 700;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================
# Header & Navigation
# =====================================================
col_h1, col_logout = st.columns([8, 2])
with col_h1:
    st.markdown('<h1 style="color: #005da7;">⚙️ Panneau d\'Administration</h1>', unsafe_allow_html=True)
with col_logout:
    if st.button("🚪 Déconnexion", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.switch_page("pages/1_Login.py")

# Sidebar navigation
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070&auto=format&fit=crop", use_container_width=True)
    st.markdown("### Menu Principal")
    # Map label to internal key
    nav_options = {
        "📊 Vue d'ensemble": "overview",
        "👥 Utilisateurs": "users",
        "🏢 Entrepôts": "warehouses",
        "🎯 Points de Livraison": "delivery_points",
        "📝 Réservations": "reservations"
    }
    
    selection = st.radio("Gestion", list(nav_options.keys()))
    admin_view = nav_options[selection]

from core.maintenance import process_inactive_users, reorder_user_ids

def render_overview():
    st.markdown('<h2 class="section-title">📊 Vue d\'ensemble</h2>', unsafe_allow_html=True)
    
    # Exécuter la maintenance automatique
    count, emails = process_inactive_users(current_user_id=st.session_state.get("user_id"))
    if count > 0:
        st.warning(f"⚠️ {count} comptes ont été suspendus pour inactivité : {', '.join(emails)}")
    
    # KPIs
    df_u = load_sql_to_dataframe("SELECT COUNT(*) as count FROM users")
    df_w = load_sql_to_dataframe("SELECT COUNT(*) as count FROM warehouses WHERE status = 'available'")
    df_r = load_sql_to_dataframe("SELECT COUNT(*) as count FROM reservations")
    
    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-value">{df_u.iloc[0]["count"]}</div><div class="kpi-label">Utilisateurs Totaux</div></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-value">{df_w.iloc[0]["count"]}</div><div class="kpi-label">Entrepôts Actifs (Dispo)</div></div>', unsafe_allow_html=True)
    with k3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-value">{df_r.iloc[0]["count"]}</div><div class="kpi-label">Réservations Totales</div></div>', unsafe_allow_html=True)
    
    st.write("")
    
    # Recent Activity
    st.markdown('<h3 class="section-title">🕒 Activité Récente</h3>', unsafe_allow_html=True)
    df_recent = load_sql_to_dataframe("SELECT reservation_id, status, created_at FROM reservations ORDER BY created_at DESC LIMIT 5")
    if not df_recent.empty:
        st.dataframe(df_recent, use_container_width=True, hide_index=True)
    else:
        st.info("Aucune activité récente.")

def render_users_page():
    st.markdown('<h2 class="section-title">👥 Gestion des Utilisateurs</h2>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Liste des Utilisateurs", "➕ Ajouter un Utilisateur"])
    
    with tab1:
        # Résumé rapide
        df_stats = load_sql_to_dataframe("SELECT is_active, COUNT(*) as count FROM users GROUP BY is_active")
        active_count = df_stats[df_stats['is_active'] == 1]['count'].sum() if not df_stats[df_stats['is_active'] == 1].empty else 0
        inactive_count = df_stats[df_stats['is_active'] == 0]['count'].sum() if not df_stats[df_stats['is_active'] == 0].empty else 0
        
        c1, c2 = st.columns(2)
        c1.metric("Comptes Actifs", active_count)
        c2.metric("Comptes Suspendus", inactive_count)
        
        # Filtre
        filter_status = st.radio("Afficher :", ["Tous", "Actifs", "Suspendus"], horizontal=True)
        
        query = "SELECT user_id, role, first_name, last_name, email, is_active, created_at FROM users"
        if filter_status == "Actifs":
            query += " WHERE is_active = 1"
        elif filter_status == "Suspendus":
            query += " WHERE is_active = 0"
            
        df_users = load_sql_to_dataframe(query)
        if not df_users.empty:
            # Transformation pour l'affichage
            df_display = df_users.copy()
            df_display['Status'] = df_display['is_active'].apply(lambda x: "✅ Actif" if x == 1 else "🚫 Suspendu")
            
            st.dataframe(df_display.drop(columns=['is_active']), use_container_width=True, hide_index=True)
            
            if st.button("🔄 Réorganiser les IDs (Fixer l'incrémentation)", help="Supprime les trous dans la suite des IDs"):
                if reorder_user_ids():
                    st.success("IDs réorganisés avec succès !")
                    st.rerun()
                else:
                    st.error("Erreur lors de la réorganisation.")

            st.markdown("### 🛠️ Actions sur les comptes")
            col_sel, col_act = st.columns([1, 1])
            
            with col_sel:
                user_email = st.selectbox("Sélectionnez l'utilisateur :", df_users['email'].tolist(), key="user_select")
                selected_user = df_users[df_users['email'] == user_email].iloc[0]
            
            with col_act:
                action_type = st.radio("Action :", ["Modifier", "Status (Actif/Inactif)", "Supprimer"], horizontal=True)
            
            if action_type == "Modifier":
                with st.form("edit_user_form"):
                    st.markdown(f"#### Modification de {user_email}")
                    c1, c2 = st.columns(2)
                    new_first = c1.text_input("Prénom", value=selected_user['first_name'])
                    new_last = c2.text_input("Nom", value=selected_user['last_name'])
                    new_email = st.text_input("Email", value=selected_user['email'])
                    new_role = st.selectbox("Rôle", ["admin", "owner", "researcher"], index=["admin", "owner", "researcher"].index(selected_user['role']))
                    
                    if st.form_submit_button("Enregistrer les modifications", type="primary"):
                        if selected_user['user_id'] == st.session_state.get("user_id") and new_role != 'admin':
                            st.error("Vous ne pouvez pas retirer vos propres droits admin.")
                        else:
                            try:
                                execute_query(
                                    "UPDATE users SET first_name=?, last_name=?, email=?, role=? WHERE user_id=?",
                                    (new_first, new_last, new_email, new_role, int(selected_user['user_id']))
                                )
                                st.success(f"Utilisateur {new_email} mis à jour avec succès !")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erreur lors de la mise à jour : {e}")
            
            elif action_type == "Status (Actif/Inactif)":
                current_status = "Actif" if selected_user['is_active'] == 1 else "Inactif"
                st.write(f"Status actuel : **{current_status}**")
                new_val = 0 if selected_user['is_active'] == 1 else 1
                label = "Désactiver" if selected_user['is_active'] == 1 else "Activer"
                
                if st.button(f"{label} le compte", type="secondary"):
                    if selected_user['user_id'] == st.session_state.get("user_id"):
                        st.error("Vous ne pouvez pas désactiver votre propre compte.")
                    else:
                        execute_query(f"UPDATE users SET is_active = {new_val} WHERE user_id = {selected_user['user_id']}")
                        st.success(f"Compte mis à jour !")
                        st.rerun()
            
            elif action_type == "Supprimer":
                st.warning("⚠️ Attention, cette action est irréversible.")
                if st.button("Confirmer la suppression", type="primary"):
                    if selected_user['user_id'] == st.session_state.get("user_id"):
                        st.error("Vous ne pouvez pas supprimer votre propre compte.")
                    else:
                        execute_query(f"DELETE FROM users WHERE user_id = {selected_user['user_id']}")
                        reorder_user_ids()
                        st.warning("Utilisateur supprimé et IDs réordonnés.")
                        st.rerun()
        else:
            st.info("Aucun utilisateur trouvé.")

    with tab2:
        with st.form("add_user_form"):
            c1, c2 = st.columns(2)
            first_name = c1.text_input("Prénom")
            last_name = c2.text_input("Nom")
            email = st.text_input("Email")
            password = st.text_input("Mot de passe", type="password")
            role = st.selectbox("Rôle", ["admin", "owner", "researcher"])
            if st.form_submit_button("Créer l'utilisateur", type="primary"):
                if first_name and last_name and email and password:
                    hashed_pw = hash_password(password)
                    now_str = get_current_time().strftime('%Y-%m-%d %H:%M:%S')
                    try:
                        execute_query(
                            "INSERT INTO users (role, first_name, last_name, email, password_hash, is_active, created_at, updated_at) VALUES (?, ?, ?, ?, ?, 1, ?, ?)",
                            (role, first_name, last_name, email, hashed_pw, now_str, now_str)
                        )
                        st.success("Utilisateur créé !")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur : {e}")
                else:
                    st.warning("Veuillez remplir tous les champs.")

def render_warehouses_page():
    st.markdown('<h2 class="section-title">🏢 Catalogue des Entrepôts</h2>', unsafe_allow_html=True)
    
    status_filter = st.selectbox("Filtrer par status", ["Tous", "Disponible", "Indisponible/Lock"], index=0)
    
    query = "SELECT warehouse_id, owner_id, name, volume_m3, latitude, longitude, status, updated_at FROM warehouses"
    if status_filter == "Disponible":
        query += " WHERE status = 'available'"
    elif status_filter == "Indisponible/Lock":
        query += " WHERE status != 'available'"
        
    df_wh = load_sql_to_dataframe(query)
    
    if not df_wh.empty:
        # Map Visualization
        st.markdown("### 📍 Localisation")
        st.map(df_wh[["latitude", "longitude"]])
        
        # Table
        st.markdown("### 📋 Détails")
        st.dataframe(df_wh, use_container_width=True, hide_index=True)
    else:
        st.info("Aucun entrepôt correspondant aux critères.")

def render_delivery_points_page():
    st.markdown('<h2 class="section-title">🎯 Points de Livraison</h2>', unsafe_allow_html=True)
    df_dp = load_sql_to_dataframe("SELECT request_id, researcher_id, name, latitude, longitude FROM delivery_points")
    if not df_dp.empty:
        st.map(df_dp[["latitude", "longitude"]])
        st.dataframe(df_dp, use_container_width=True, hide_index=True)
    else:
        st.info("Aucun point de livraison enregistré.")

def render_reservations_page():
    st.markdown('<h2 class="section-title">📝 Suivi des Réservations</h2>', unsafe_allow_html=True)
    Reservation._purger_verrous_expires_cls()
    df_res = load_sql_to_dataframe("SELECT * FROM reservations ORDER BY created_at DESC")
    if not df_res.empty:
        st.dataframe(df_res, use_container_width=True, hide_index=True)
        
        st.divider()
        st.subheader("⚙️ Actions Administratives")
        res_id = st.selectbox("ID Réservation à modifier", df_res['reservation_id'].tolist())
        action = st.radio("Changer status en :", ["Confirmer (Final)", "Annuler (Libérer)"], horizontal=True)
        
        if st.button("Appliquer", type="primary"):
            new_status = "confirmed" if "Confirmer" in action else "canceled"
            execute_query(f"UPDATE reservations SET status = '{new_status}', reason = 'Action administrative' WHERE reservation_id = '{res_id}'")
            
            # Mettre à jour le warehouse
            df_target = load_sql_to_dataframe(f"SELECT warehouse_id FROM reservations WHERE reservation_id = '{res_id}'")
            if not df_target.empty:
                w_id = df_target.iloc[0]["warehouse_id"]
                w_status = 'unavailable' if new_status == 'confirmed' else 'available'
                execute_query(f"UPDATE warehouses SET status = ? WHERE warehouse_id = ?", (w_status, w_id))
            
            st.success(f"Réservation {res_id} mise à jour !")
            st.rerun()
    else:
        st.info("Aucune réservation.")

# =====================================================
# Main Dispatcher
# =====================================================
try:
    if admin_view == "overview":
        render_overview()
    elif admin_view == "users":
        render_users_page()
    elif admin_view == "warehouses":
        render_warehouses_page()
    elif admin_view == "delivery_points":
        render_delivery_points_page()
    elif admin_view == "reservations":
        render_reservations_page()
    else:
        st.write(f"Vue inconnue : {admin_view}")
except Exception as e:
    st.error(f"⚠️ Une erreur est survenue lors de l'affichage de la page : {e}")
    st.exception(e)
