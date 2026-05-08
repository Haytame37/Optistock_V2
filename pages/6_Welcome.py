import streamlit as st
from utils.ui import hide_sidebar

# =====================================================
# Configuration
# =====================================================
st.set_page_config(
    page_title="OptiStock – Bienvenue",
    page_icon="📦",
    layout="wide"
)
hide_sidebar()

# =====================================================
# CSS
# =====================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Work+Sans:wght@800;900&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #f0f7ff 0%, #e8f4fd 50%, #f0fdf4 100%) !important;
    font-family: 'Inter', sans-serif;
}

.header {
    position: fixed; top: 0; left: 0; width: 100%;
    background: rgba(255,255,255,0.92); backdrop-filter: blur(10px);
    border-bottom: 1px solid #dbe7f3; padding: 14px 32px;
    display: flex; justify-content: space-between; align-items: center;
    z-index: 999;
}
.brand {
    font-family: 'Work Sans', sans-serif; font-weight: 900;
    font-size: 22px; color: #005da7;
}
.hero-badge {
    display: inline-block;
    background: linear-gradient(90deg, #dbeafe, #dcfce7);
    color: #1e40af; font-size: 12px; font-weight: 700;
    padding: 5px 14px; border-radius: 999px;
    border: 1px solid #bfdbfe; margin-bottom: 20px;
    letter-spacing: 0.5px;
}
.card-choice {
    background: white;
    border-radius: 20px;
    border: 1.5px solid #e2e8f0;
    padding: 36px 32px;
    box-shadow: 0 8px 32px rgba(0,93,167,0.08);
    transition: transform 0.2s, box-shadow 0.2s;
    height: 100%;
}
.card-choice:hover {
    transform: translateY(-4px);
    box-shadow: 0 16px 48px rgba(0,93,167,0.15);
}
.divider-or {
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; font-weight: 700; color: #94a3b8;
    padding: 0 16px;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# Header fixe
# =====================================================
st.markdown("""
<div class="header">
    <div class="brand">📦 OptiStock</div>
    <div style="font-size:13px;color:#64748b;">Plateforme logistique intelligente</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:80px'></div>", unsafe_allow_html=True)

# =====================================================
# Hero Section
# =====================================================
st.markdown("""
<div style="text-align:center; padding: 40px 20px 30px;">
    <div class="hero-badge">🚀 Plateforme IoT & Logistique</div>
    <h1 style="
        font-family: 'Work Sans', sans-serif;
        font-size: clamp(2rem, 4vw, 3rem);
        font-weight: 900;
        color: #0f172a;
        margin: 0 0 16px;
        line-height: 1.2;
    ">
        L'intelligence au service<br>de votre logistique
    </h1>
    <p style="
        font-size: 1.1rem;
        color: #475569;
        max-width: 580px;
        margin: 0 auto 40px;
        line-height: 1.7;
    ">
        Connectez-vous pour superviser vos inventaires en temps réel,
        analyser vos données logistiques et prendre les meilleures décisions.
    </p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# Cartes de choix
# =====================================================
col_left, col_mid, col_right = st.columns([5, 1, 5], gap="small")

with col_left:
    st.markdown("""
    <div class="card-choice">
        <div style="font-size: 44px; margin-bottom: 14px;">🔐</div>
        <h3 style="color:#005da7; font-family:'Work Sans',sans-serif;
                   font-weight:800; margin:0 0 10px; font-size:1.4rem;">
            Se connecter
        </h3>
        <p style="color:#475569; font-size:14px; line-height:1.6; margin:0 0 24px;">
            Accédez à votre espace personnel. Gérez vos entrepôts,
            suivez vos données IoT et consultez vos analyses logistiques.
        </p>
        <ul style="color:#64748b; font-size:13px; line-height:2; padding-left:18px; margin:0 0 28px;">
            <li>Tableau de bord personnalisé</li>
            <li>Suivi IoT en temps réel</li>
            <li>Messagerie avec les partenaires</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    st.write("")
    if st.button("🔐 Se connecter", type="primary", use_container_width=True, key="btn_login"):
        st.switch_page("pages/1_Login.py")

with col_mid:
    st.markdown("""
    <div class="divider-or" style="height:100%;min-height:280px;">
        <div style="writing-mode:vertical-lr;text-orientation:mixed;
                    color:#cbd5e1;font-size:13px;letter-spacing:2px;">
            OU
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown("""
    <div class="card-choice" style="border-color:#bbf7d0;">
        <div style="font-size: 44px; margin-bottom: 14px;">✨</div>
        <h3 style="color:#15803d; font-family:'Work Sans',sans-serif;
                   font-weight:800; margin:0 0 10px; font-size:1.4rem;">
            Créer un compte
        </h3>
        <p style="color:#475569; font-size:14px; line-height:1.6; margin:0 0 24px;">
            Rejoignez OptiStock et accédez à toutes les fonctionnalités
            de notre plateforme logistique intelligente.
        </p>
        <ul style="color:#64748b; font-size:13px; line-height:2; padding-left:18px; margin:0 0 28px;">
            <li>Inscription rapide et gratuite</li>
            <li>Accès immédiat après création</li>
            <li>Chercheur ou Propriétaire d'entrepôt</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    st.write("")
    if st.button("✨ Créer un compte", use_container_width=True, key="btn_signup"):
        st.switch_page("pages/2_Signup.py")

# =====================================================
# Lien retour accueil
# =====================================================
st.write("")
st.markdown("<div style='text-align:center'>", unsafe_allow_html=True)
if st.button("← Retour à l'accueil", key="btn_home"):
    st.switch_page("app.py")
st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# Footer
# =====================================================
st.markdown("""
<div style="margin-top:48px;padding:20px;border-top:1px solid #e1e5ea;
            text-align:center;font-size:13px;color:#9ca3af;">
    © 2026 OptiStock Logistics Intelligence — Tous droits réservés
</div>
""", unsafe_allow_html=True)
