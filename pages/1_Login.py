import streamlit as st

# =====================================================
# Configuration de la page
# =====================================================
st.set_page_config(
    page_title="OptiStock – Connexion",
    page_icon="🔐",
    layout="wide"
)

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
# Carte de connexion (Format Desktop)
# =====================================================
col_img, col_form = st.columns([1.2, 1], gap="large")

with col_img:
    st.markdown('''
    <div style="padding-top: 40px; padding-left: 20px;">
        <h2 style="color: #005da7; font-size: 2rem;">L'intelligence au service de votre logistique</h2>
        <p style="color: #555d64; font-size: 1.1rem; margin-bottom: 24px;">Connectez-vous pour superviser vos inventaires en temps réel, analyser vos données logistiques et prendre les meilleures décisions.</p>
    </div>
    ''', unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1580674285054-bed31e145f59?q=80&w=2070&auto=format&fit=crop", use_container_width=True)

with col_form:
    st.markdown('<div class="login-card" style="max-width: 500px; margin: 0 auto;">', unsafe_allow_html=True)

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
        submit = st.button("🔐 Se connecter", use_container_width=True)

    with col_btn2:
        if st.button("❓ Mot de passe oublié"):
            st.info("Lien de récupération envoyé par email (simulé)")

    if submit:
        if not email or not password:
            st.error("Veuillez renseigner votre email et votre mot de passe")
        else:
            from core.auth import authenticate_user
            user = authenticate_user(email, password)
            
            if user:
                if user['is_active'] == 0:
                    st.error("❌ Votre compte est désactivé.")
                else:
                    st.success(f"✅ Bienvenue {user['first_name']} ! Connexion réussie.")
                    st.session_state['user'] = user
                    st.session_state['user_id'] = user['user_id']
                    st.session_state['role'] = user['role']
                    st.session_state['logged_in'] = True
                    
                    if user['role'] == 'admin':
                        st.switch_page("pages/2_Dashboard_Admin.py")
                    elif user['role'] == 'researcher':
                        st.switch_page("pages/3_Interface_Chercheur.py")
                    elif user['role'] == 'owner':
                        st.switch_page("pages/4_Interface_Proprietaire.py")
            else:
                st.error("❌ Identifiants incorrects.")

    st.markdown("---")
    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.markdown("<p style='margin-top: 8px;'>Pas encore de compte ?</p>", unsafe_allow_html=True)
    with col2:
        if st.button("Créer un compte", use_container_width=True):
            st.switch_page("pages/Signup.py")

    st.markdown("</div>", unsafe_allow_html=True)

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
