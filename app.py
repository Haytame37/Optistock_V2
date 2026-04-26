import streamlit as st
import base64
import os

# Configuration de la page
st.set_page_config(
    page_title="OptiStock Solutions",
    page_icon="📦",
    layout="wide"
)

# Injection du CSS personnalisé pour correspondre au design HTML
st.markdown("""
    <style>
    /* Import des polices */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Work+Sans:wght@600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

    /* Variables de couleurs */
    :root {
        --primary: #005da7;
        --secondary-container: #fe893a;
        --background: #f4fafd;
        --text-main: #161d1f;
    }

    /* Arrière-plan "Circuit" */
    .stApp {
        background-color: #f4fafd;
        background-image: 
            radial-gradient(#d1e2f3 1px, transparent 1px),
            linear-gradient(to right, #d1e2f3 1px, transparent 1px),
            linear-gradient(to bottom, #d1e2f3 1px, transparent 1px);
        background-size: 40px 40px, 80px 80px, 80px 80px;
    }

    /* Style du titre */
    .hero-title {
        font-family: 'Work Sans', sans-serif;
        color: var(--primary);
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        line-height: 1.2;
        margin-bottom: 0.5rem;
    }

    .hero-subtitle {
        font-family: 'Inter', sans-serif;
        color: #555d64;
        font-size: 1.2rem;
        text-align: center;
        margin-bottom: 2rem;
    }

    /* Cartes de fonctionnalités */
    .feature-card {
        background: white;
        border: 1px solid #D1E2F3;
        padding: 24px;
        border-radius: 12px;
        text-align: center;
        height: 100%;
        transition: transform 0.2s;
    }
    
    .feature-icon {
        background: #d4e3ff;
        color: var(--primary);
        width: 48px;
        height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 8px;
        margin: 0 auto 15px auto;
    }

    /* Boutons personnalisés */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.6rem 2rem;
        transition: all 0.2s;
    }

    .btn-login > div > button {
        background-color: var(--primary) !important;
        color: white !important;
        border: none !important;
    }

    .btn-signup > div > button {
        background-color: var(--secondary-container) !important;
        color: #672d00 !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Header ---
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

col_logo, _ = st.columns([2, 3])
with col_logo:
    img_path = "image_6c8213.png"
    if os.path.exists(img_path):
        b64_logo = get_base64_image(img_path)
        logo_html = f'<img src="data:image/png;base64,{b64_logo}" style="height: 40px; margin-right: 10px;">'
    else:
        logo_html = '<span class="material-symbols-outlined" style="color: #005da7; font-size: 32px; margin-right: 10px;">hub</span>'

    st.markdown(f"""
        <div style="display: flex; align-items: center; margin-bottom: 20px;">
            {logo_html}
            <span style="font-weight: bold; font-size: 20px; color: #005da7;">OptiStock Solutions</span>
        </div>
    """, unsafe_allow_html=True)

# --- Hero Section ---
st.markdown('<h1 class="hero-title">Optimisation intelligente des centres de stockage logistique</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Gestion intelligente des entrepôts</p>', unsafe_allow_html=True)

# --- Feature Grid (2x2) ---
features = [
    {"icon": "sensors", "text": "Surveillance d'entrepôt en temps réel"},
    {"icon": "hub", "text": "Optimisation de la logistique"},
    {"icon": "ac_unit", "text": "Contrôle de l'intégrité des produits"},
    {"icon": "inventory_2", "text": "Gestion des actifs d'entrepôt"}
]

# Création de la grille avec les colonnes Streamlit
col1, col2 = st.columns(2)

for i, feature in enumerate(features):
    target_col = col1 if i % 2 == 0 else col2
    with target_col:
        st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon">
                    <span class="material-symbols-outlined" style="font-size: 30px;">{feature['icon']}</span>
                </div>
                <div style="font-weight: 600; font-size: 14px; line-height: 1.4;">{feature['text']}</div>
            </div>
        """, unsafe_allow_html=True)
        st.write("") # Espacement vertical

# --- Illustration Section ---
st.write("")
st.image("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070&auto=format&fit=crop", 
         caption="Modern high-tech warehouse interior", 
         use_container_width=True)

# --- Bottom Navigation / Actions ---
st.markdown("---")
col_login, col_signup = st.columns(2)

with col_login:
    st.markdown('<div class="btn-login">', unsafe_allow_html=True)
    if st.button("Commencer maintenant"):
        st.switch_page("pages/1_Login.py")
    st.markdown('</div>', unsafe_allow_html=True)

with col_signup:
    st.markdown('<div class="btn-signup">', unsafe_allow_html=True)
    if st.button("Voir la démo"):
        st.success("Bienvenue à bord !")
    st.markdown('</div>', unsafe_allow_html=True)