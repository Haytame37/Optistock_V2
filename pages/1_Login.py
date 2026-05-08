import streamlit as st

# =====================================================
# Configuration de la page
# =====================================================
from utils.ui import hide_sidebar
st.set_page_config(
    page_title="OptiStock – Connexion",
    page_icon="🔐",
    layout="wide"
)
hide_sidebar()

# =====================================================
# CSS léger (équivalent Tailwind)
# =====================================================
st.markdown("""
<style>
body {
    font-family: Inter, sans-serif;
    background-color: #f4fafd;
}

.header {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    background: rgba(255,255,255,0.9);
    backdrop-filter: blur(6px);
    border-bottom: 1px solid #dbe7f3;
    padding: 16px;
    display: flex;
    justify-content: center;
    z-index: 999;
}

.brand {
    font-family: 'Work Sans', sans-serif;
    font-weight: 900;
    font-size: 24px;
    color: #005da7;
}

.login-card {
    background: white;
    padding: 32px;
    border-radius: 16px;
    border: 1px solid #dbe7f3;
    box-shadow: 0 10px 24px rgba(0,96,172,0.08);
    width: 100%;
    max-width: 420px;
}

.footer {
    margin-top: 48px;
    padding: 24px;
    border-top: 1px solid #e1e5ea;
    text-align: center;
    font-size: 13px;
    color: #6b7280;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# Header
# =====================================================
st.markdown("""
<div class="header">
    <div class="brand">OptiStock</div>
</div>
""", unsafe_allow_html=True)

# Espace sous le header fixe
st.markdown("<div style='height:90px'></div>", unsafe_allow_html=True)

# =====================================================
# Carte de connexion centrée
# =====================================================
_, col_form, _ = st.columns([1, 1.4, 1])

with col_form:
    with st.container(border=True):
        st.markdown("## 👋 Bon retour")
        st.caption("Connectez-vous pour gérer votre chaîne logistique")

        email = st.text_input(
            "Adresse e-mail",
            placeholder="nom@entreprise.com"
        )

        password = st.text_input(
            "Mot de passe",
            type="password",
            placeholder="••••••••"
        )

        col_btn1, col_btn2 = st.columns([2, 1])
        with col_btn1:
            submit = st.button("🔐 Se connecter", use_container_width=True, type="primary")

        with col_btn2:
            if st.button("❓ Mot de passe oublié"):
                st.switch_page("pages/5_Forgot_Password.py")

        if submit:
            if not email or not password:
                st.error("Veuillez renseigner votre email et votre mot de passe")
            else:
                from core.auth import authenticate_user
                from utils.db import load_sql_to_dataframe
                result = authenticate_user(email, password)

                def redirect_user(user):
                    """Redirige l'utilisateur — vers changement mdp si temporaire, sinon dashboard."""
                    st.session_state['user']      = user
                    st.session_state['user_id']   = user['user_id']
                    st.session_state['role']      = user['role']
                    st.session_state['logged_in'] = True
                    # Vérifier le flag must_change_password
                    df = load_sql_to_dataframe(
                        "SELECT must_change_password FROM users WHERE user_id = ?",
                        (user['user_id'],)
                    )
                    must_change = (not df.empty and df.iloc[0]['must_change_password'] == 1)
                    if must_change:
                        st.switch_page("pages/7_Change_Password.py")
                    elif user['role'] == 'admin':
                        st.switch_page("pages/3_Dashboard_Admin.py")
                    elif user['role'] == 'researcher':
                        st.switch_page("pages/9_Interface_Chercheur.py")
                    elif user['role'] == 'owner':
                        st.switch_page("pages/4_Interface_Proprietaire.py")

                if result is None:
                    st.error("❌ Identifiants incorrects.")

                elif isinstance(result, list):
                    st.info("🔀 Plusieurs comptes sont associés à cet email. Choisissez votre profil :")
                    role_labels = {
                        "admin":      "⚙️ Administrateur",
                        "owner":      "🏢 Propriétaire d'entrepôt",
                        "researcher": "🔍 Chercheur d'entrepôt",
                    }
                    options = {
                        f"{role_labels.get(acc['role'], acc['role'])} — {acc['first_name']} {acc['last_name']}": acc
                        for acc in result
                    }
                    chosen_label = st.selectbox("Sélectionnez votre compte :", list(options.keys()), key="multi_account_select")
                    if st.button("✅ Confirmer et se connecter", type="primary", use_container_width=True):
                        redirect_user(options[chosen_label])

                else:
                    user = result
                    if user['is_active'] == 0:
                        st.error("❌ Votre compte est désactivé.")
                    else:
                        st.success(f"✅ Bienvenue {user['first_name']} ! Connexion réussie.")
                        redirect_user(user)


        st.markdown("---")
        col1, col2 = st.columns([1, 1.2])
        with col1:
            st.markdown("<p style='margin-top: 8px;'>Pas encore de compte ?</p>", unsafe_allow_html=True)
        with col2:
            if st.button("Créer un compte", use_container_width=True):
                st.switch_page("pages/2_Signup.py")

# =====================================================
# Footer
# =====================================================
st.markdown("""
<div class="footer">
    © 2026 OptiStock Logistics Intelligence — Tous droits réservés<br/>
    <a href="#">Politique de confidentialité</a> •
    <a href="#">Conditions d'utilisation</a> •
    <a href="#">Support</a>
</div>
""", unsafe_allow_html=True)
