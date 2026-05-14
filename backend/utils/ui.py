"""
Utilitaire UI global - OptiStock
"""
import streamlit as st


HIDE_SIDEBAR_CSS = """
<style>
/* Masquer complètement la sidebar Streamlit */
[data-testid="stSidebar"]          { display: none !important; }
[data-testid="collapsedControl"]   { display: none !important; }
[data-testid="stSidebarNav"]       { display: none !important; }
section[data-testid="stSidebar"]   { display: none !important; }
.st-emotion-cache-1cypcdb          { display: none !important; }
/* Etendre le contenu sur toute la largeur */
.block-container { max-width: 100% !important; padding-left: 2rem !important; padding-right: 2rem !important; }
</style>
"""


def hide_sidebar() -> None:
    """Supprime complètement la sidebar Streamlit de la page courante."""
    st.markdown(HIDE_SIDEBAR_CSS, unsafe_allow_html=True)
