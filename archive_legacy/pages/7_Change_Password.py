import streamlit as st
import re
from utils.ui import hide_sidebar
from utils.db import execute_query
from core.auth import hash_password

# =====================================================
# Sécurité — doit être connecté
# =====================================================
st.set_page_config(
    page_title="OptiStock – Changer le mot de passe",
    page_icon="🔒",
    layout="wide"
)
hide_sidebar()

if "user_id" not in st.session_state or not st.session_state.get("logged_in"):
    st.switch_page("pages/1_Login.py")

user_id    = st.session_state["user_id"]
first_name = st.session_state.get("user", {}).get("first_name", "")

# =====================================================
# CSS
# =====================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Work+Sans:wght@800;900&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: #f4f8fc !important;
    font-family: 'Inter', sans-serif;
}
.header {
    position: fixed; top: 0; left: 0; width: 100%;
    background: rgba(255,255,255,0.92); backdrop-filter: blur(10px);
    border-bottom: 1px solid #dbe7f3; padding: 14px 32px;
    display: flex; justify-content: center; z-index: 999;
}
.brand { font-family: 'Work Sans', sans-serif; font-weight: 900; font-size: 22px; color: #005da7; }

.strength-track {
    background: #e2e8f0; border-radius: 4px; height: 6px; margin: 6px 0 10px; overflow: hidden;
}
.strength-fill { height: 6px; border-radius: 4px; }
.rule-ok   { color: #16a34a; font-weight: 700; }
.rule-fail { color: #dc2626; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header"><div class="brand">📦 OptiStock</div></div>
""", unsafe_allow_html=True)
st.markdown("<div style='height:80px'></div>", unsafe_allow_html=True)

# =====================================================
# Fonctions
# =====================================================
def check_rules(pwd):
    return {
        "8 caractères minimum":          len(pwd) >= 8,
        "Au moins une MAJUSCULE":        bool(re.search(r'[A-Z]', pwd)),
        "Au moins une minuscule":        bool(re.search(r'[a-z]', pwd)),
        "Au moins un chiffre":           bool(re.search(r'\d', pwd)),
        "Au moins un caractère spécial": bool(re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>/?]', pwd)),
        "Pas d'espace":                  ' ' not in pwd,
    }

def strength(rules):
    score = sum(rules.values())
    if score <= 2: return score, "Très faible", "#dc2626"
    if score == 3: return score, "Faible",      "#f97316"
    if score == 4: return score, "Moyen",       "#eab308"
    if score == 5: return score, "Fort",        "#22c55e"
    return score,  "Très fort 🔒",              "#16a34a"

# =====================================================
# UI
# =====================================================
_, col, _ = st.columns([1, 1.6, 1])

with col:
    # Bandeau simple
    st.markdown(f"""
    <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:12px;
                padding:14px 18px;margin-bottom:16px;">
        <div style="font-size:14px;color:#1e40af;font-weight:600;">🔒 Réinitialisation du mot de passe</div>
        <div style="font-size:13px;color:#3b82f6;margin-top:3px;">
            Bonjour <b>{first_name}</b>, veuillez définir un nouveau mot de passe pour accéder à votre espace.
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("### 🔑 Nouveau mot de passe")

        new_pwd = st.text_input(
            "Nouveau mot de passe",
            type="password",
            placeholder="••••••••",
            key="new_pwd"
        )

        # Widget force en temps réel
        if new_pwd:
            rules = check_rules(new_pwd)
            sc, label, color = strength(rules)
            pct = int(sc / 6 * 100)
            ok_icon   = '<span class="rule-ok">✓</span>'
            fail_icon = '<span class="rule-fail">✗</span>'
            rules_html = "".join([
                f'<div style="font-size:12px;color:#475569;padding:2px 0;">'
                f'{ok_icon if ok else fail_icon} {rule}</div>'
                for rule, ok in rules.items()
            ])
            st.markdown(f"""
            <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:10px 14px;margin-bottom:8px;">
                <div style="font-size:12px;font-weight:700;color:{color};margin-bottom:4px;">Force : {label} ({sc}/6)</div>
                <div class="strength-track">
                    <div class="strength-fill" style="width:{pct}%;background:{color};"></div>
                </div>
                {rules_html}
            </div>
            """, unsafe_allow_html=True)

        confirm_pwd = st.text_input(
            "Confirmer le mot de passe",
            type="password",
            placeholder="••••••••",
            key="confirm_pwd"
        )

        if new_pwd and confirm_pwd:
            if new_pwd == confirm_pwd:
                st.success("✅ Les mots de passe correspondent.")
            else:
                st.error("❌ Les mots de passe ne correspondent pas.")

        st.write("")
        if st.button("💾 Enregistrer le nouveau mot de passe", type="primary", use_container_width=True):
            errors = []
            if not new_pwd:
                errors.append("Le mot de passe est obligatoire.")
            else:
                rules = check_rules(new_pwd)
                failed = [r for r, ok in rules.items() if not ok]
                if failed:
                    errors.append("Règles non respectées : " + ", ".join(failed))
            if new_pwd and confirm_pwd and new_pwd != confirm_pwd:
                errors.append("Les mots de passe ne correspondent pas.")

            if errors:
                for e in errors:
                    st.error(f"❌ {e}")
            else:
                new_hash = hash_password(new_pwd)
                execute_query(
                    "UPDATE users SET password_hash = ?, must_change_password = 0 WHERE user_id = ?",
                    (new_hash, str(user_id))
                )
                st.success("✅ Mot de passe mis à jour avec succès !")
                role = st.session_state.get("role", "")
                pages = {
                    'admin':      "pages/3_Dashboard_Admin.py",
                    'researcher': "pages/9_Interface_Chercheur.py",
                    'owner':      "pages/4_Interface_Proprietaire.py",
                }
                st.switch_page(pages.get(role, "pages/1_Login.py"))
