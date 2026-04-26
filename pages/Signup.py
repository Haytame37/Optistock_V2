import streamlit as st

# =====================================================
# Configuration de la page
# =====================================================
st.set_page_config(
    page_title="OptiStock – Inscription",
    page_icon="📝",
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
# Carte d'inscription (Format Desktop)
# =====================================================
st.write("") # Espacement vertical
col_img, col_form = st.columns([1.2, 1], gap="large")

with col_img:
    st.markdown('''
    <div style="padding-top: 40px; padding-left: 20px;">
        <h2 style="color: #005da7; font-size: 2rem;">Rejoignez la révolution logistique</h2>
        <p style="color: #555d64; font-size: 1.1rem; margin-bottom: 24px;">Créez votre compte pour optimiser vos flux de stockage et rejoindre les leaders de l'industrie pour une gestion intelligente.</p>
    </div>
    ''', unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1553413077-190dd305871c?q=80&w=2000&auto=format&fit=crop", use_container_width=True)

with col_form:
    st.markdown('<div class="login-card" style="max-width: 500px; margin: 0 auto;">', unsafe_allow_html=True)

    st.markdown("## 📝 Créer un compte")
    st.caption("Rejoignez OptiStock Logistics Intelligence")

    st.write("")

    nom = st.text_input(
        "Nom complet",
        placeholder="Votre nom"
    )

    email = st.text_input(
        "Adresse e-mail",
        placeholder="nom@entreprise.com"
    )

    role = st.selectbox(
        "Sélectionnez votre profil",
        options=["Propriétaire d'entrepôt", "Chercheur d'entrepôt"]
    )

    password = st.text_input(
        "Mot de passe",
        type="password",
        placeholder="••••••••"
    )

    password_confirm = st.text_input(
        "Confirmer le mot de passe",
        type="password",
        placeholder="••••••••"
    )

    if st.button("🚀 S'inscrire", use_container_width=True):
        if not nom or not email or not password or not password_confirm:
            st.error("Veuillez remplir tous les champs")
        elif password != password_confirm:
            st.error("Les mots de passe ne correspondent pas")
        else:
            role_map = {
                "Propriétaire d'entrepôt": "owner",
                "Chercheur d'entrepôt": "researcher",
                "Administrateur": "admin"
            }
            db_role = role_map.get(role, "owner")
            
            parts = nom.split(" ", 1)
            first_name = parts[0]
            last_name = parts[1] if len(parts) > 1 else ""
            
            from core.auth import create_user
            success = create_user(db_role, first_name, last_name, email, password)
            if success:
                st.success("✅ Compte créé avec succès !")
                st.info("Vous pouvez maintenant vous connecter.")
            else:
                st.error("Erreur : Adresse e-mail déjà utilisée ou problème serveur.")

    st.markdown("---")
    
    st.write("Vous avez déjà un compte ?")
    if st.button("Se connecter", use_container_width=True):
        st.switch_page("pages/1_Login.py")

    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# Footer
# =====================================================
st.markdown("""
<div class="footer">
    © 2024 OptiStock Logistics Intelligence — Tous droits réservés<br/>
    <a href="#">Politique de confidentialité</a> •
    <a href="#">Conditions d'utilisation</a> •
    <a href="#">Support</a>
</div>
""", unsafe_allow_html=True)
