import streamlit as st
import bcrypt
from utils.db import load_sql_to_dataframe

st.set_page_config(page_title="OptiStock - Login", page_icon="🔐", layout="centered")

st.title("🔐 Connexion OptiStock")
st.markdown("Veuillez vous authentifier pour accéder à votre espace.")

with st.form("login_form"):
    email = st.text_input("Adresse Email")
    password = st.text_input("Mot de passe", type="password")
    submit = st.form_submit_button("Se connecter", type="primary")

if submit:
    if email and password:
        df_user = load_sql_to_dataframe(f"SELECT * FROM users WHERE email = '{email}' AND is_active = 1")
        if not df_user.empty:
            user = df_user.iloc[0]
            # Vérification du mot de passe avec BCrypt
            if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                st.session_state["user_id"] = user["user_id"]
                st.session_state["role"] = user["role"]
                st.session_state["first_name"] = user["first_name"]
                st.session_state["last_name"] = user["last_name"]
                st.success(f"Bienvenue {user['first_name']} {user['last_name']} ! Vous êtes connecté en tant que {user['role']}.")
                st.info("Veuillez utiliser le menu de gauche pour naviguer vers votre interface dédiée.")
            else:
                st.error("Mot de passe incorrect.")
        else:
            st.error("Email incorrect ou compte inactif.")
    else:
        st.warning("Veuillez remplir tous les champs.")
