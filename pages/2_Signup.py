import streamlit as st
import re

# =====================================================
# Configuration de la page
# =====================================================
st.set_page_config(
    page_title="OptiStock – Inscription",
    page_icon="📝",
    layout="wide"
)

# =====================================================
# CSS
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

/* Règles de mot de passe */
.pwd-rules {
    background: #f0f7ff;
    border-left: 4px solid #005da7;
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    margin: 8px 0 12px 0;
    font-size: 13px;
    color: #334155;
}
.pwd-rules ul {
    margin: 6px 0 0 0;
    padding-left: 18px;
}
.pwd-rules ul li { margin-bottom: 3px; }

/* Widget de force du mot de passe */
.strength-widget {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 10px 14px;
    margin: 6px 0 12px 0;
}
.strength-label {
    font-size: 13px;
    font-weight: 700;
    margin-bottom: 6px;
}
.strength-track {
    background: #e2e8f0;
    border-radius: 4px;
    height: 7px;
    margin-bottom: 10px;
    overflow: hidden;
}
.strength-fill {
    height: 7px;
    border-radius: 4px;
}
.rules-detail {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2px 12px;
}
.rule-row {
    font-size: 12px;
    color: #475569;
    padding: 2px 0;
}
.rule-ok   { color: #16a34a; font-weight: 700; }
.rule-fail { color: #dc2626; font-weight: 700; }
.rule-empty { color: #94a3b8; font-weight: 700; }

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
# Fonctions de validation
# =====================================================
def validate_email(email: str) -> tuple[bool, str]:
    """
    Valide le format d'une adresse e-mail selon RFC 5322 simplifié.
    Exige: local@domaine.extension (extension ≥ 2 chars)
    """
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    if not email:
        return False, "L'adresse e-mail est obligatoire."
    if not re.match(pattern, email):
        return False, "Format invalide. Exemple attendu : nom@entreprise.com"
    if email.count('@') != 1:
        return False, "L'adresse ne doit contenir qu'un seul '@'."
    local, domain = email.split('@')
    if len(local) < 1:
        return False, "La partie locale (avant @) est vide."
    if '.' not in domain:
        return False, "Le domaine doit contenir un point (ex: entreprise.com)."
    return True, "✅ Format e-mail valide."


def check_password_rules(pwd: str) -> dict:
    """
    Vérifie chaque règle de robustesse du mot de passe.
    Retourne un dict {règle: bool}.
    """
    return {
        "8 caractères minimum":          len(pwd) >= 8,
        "Au moins une MAJUSCULE (A-Z)":  bool(re.search(r'[A-Z]', pwd)),
        "Au moins une minuscule (a-z)":  bool(re.search(r'[a-z]', pwd)),
        "Au moins un chiffre (0-9)":     bool(re.search(r'\d', pwd)),
        "Au moins un caractère spécial (!@#$%^&*…)": bool(re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', pwd)),
        "Pas d'espace":                  ' ' not in pwd,
    }


def password_strength(rules: dict) -> tuple[int, str, str]:
    """
    Retourne (score 0-6, label, couleur CSS).
    """
    score = sum(rules.values())
    if score <= 2:
        return score, "Très faible", "#dc2626"
    if score == 3:
        return score, "Faible", "#f97316"
    if score == 4:
        return score, "Moyen", "#eab308"
    if score == 5:
        return score, "Fort", "#22c55e"
    return score, "Très fort 🔒", "#16a34a"


# =====================================================
# Header
# =====================================================
st.markdown("""
<div class="header">
    <div class="brand">OptiStock</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:90px'></div>", unsafe_allow_html=True)

# Désactiver le gestionnaire de mots de passe du navigateur
st.markdown("""
<script>
(function() {
    function disablePwdManager() {
        document.querySelectorAll('input[type="password"]').forEach(function(el) {
            el.setAttribute('autocomplete', 'new-password');
            el.setAttribute('data-lpignore', 'true');
            el.setAttribute('data-form-type', 'other');
        });
    }
    // Exécuter au chargement et après chaque mutation DOM (Streamlit rerenders)
    disablePwdManager();
    new MutationObserver(disablePwdManager).observe(document.body, {childList: true, subtree: true});
})();
</script>
""", unsafe_allow_html=True)

# =====================================================
# Mise en page
# =====================================================
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

    # ── Nom complet ──────────────────────────────────
    nom = st.text_input("Nom complet", placeholder="Prénom Nom")

    # ── E-mail avec validation en temps réel ─────────
    email = st.text_input("Adresse e-mail", placeholder="nom@entreprise.com")

    if email:
        email_ok, email_msg = validate_email(email)
        if email_ok:
            st.success(email_msg)
        else:
            st.error(f"❌ {email_msg}")
    else:
        st.caption("📧 Format attendu : **nom@domaine.extension** (ex: jean.dupont@optistock.com)")

    # ── Rôle ─────────────────────────────────────────
    role = st.selectbox(
        "Sélectionnez votre profil",
        options=["Propriétaire d'entrepôt", "Chercheur d'entrepôt"]
    )

    # ── Mot de passe ─────────────────────────────────
    password = st.text_input(
        "Mot de passe",
        type="password",
        placeholder="••••••••",
        key="pwd_input",
        autocomplete="new-password"
    )

    # ── Indicateur de force en temps réel (toujours visible) ──────────────────
    if password:
        rules = check_password_rules(password)
        score, label, color = password_strength(rules)
        pct = int(score / 6 * 100)

        # Construire les lignes HTML des règles
        rules_html = "".join([
            f'<div class="rule-row">{"<span class=\"rule-ok\">&#10003;</span>" if ok else "<span class=\"rule-fail\">&#10007;</span>"} {rule}</div>'
            for rule, ok in rules.items()
        ])

        st.markdown(f"""
<div class="strength-widget">
    <div class="strength-label" style="color:{color};">Force : {label} ({score}/6)</div>
    <div class="strength-track">
        <div class="strength-fill" style="width:{pct}%; background:{color};"></div>
    </div>
    <div class="rules-detail">
        {rules_html}
    </div>
</div>
""", unsafe_allow_html=True)
    else:
        # Afficher les règles vides (toutes grises) quand rien n'est saisi
        empty_rules = list(check_password_rules("").keys())
        rules_html = "".join([
            f'<div class="rule-row"><span class="rule-empty">&minus;</span> {r}</div>'
            for r in empty_rules
        ])
        st.markdown(f"""
<div class="strength-widget">
    <div class="strength-label" style="color:#94a3b8;">Force : — (0/6)</div>
    <div class="strength-track">
        <div class="strength-fill" style="width:0%; background:#94a3b8;"></div>
    </div>
    <div class="rules-detail">
        {rules_html}
    </div>
</div>
""", unsafe_allow_html=True)

    password_confirm = st.text_input(
        "Confirmer le mot de passe",
        type="password",
        placeholder="••••••••",
        key="pwd_confirm_input",
        autocomplete="new-password"
    )

    # Vérification correspondance en temps réel
    if password and password_confirm:
        if password == password_confirm:
            st.success("✅ Les mots de passe correspondent.")
        else:
            st.error("❌ Les mots de passe ne correspondent pas.")


    # ── Bouton S'inscrire ─────────────────────────────
    if st.button("🚀 S'inscrire", use_container_width=True, type="primary"):
        errors = []

        if not nom or not nom.strip():
            errors.append("Le nom complet est obligatoire.")

        email_ok, email_msg = validate_email(email)
        if not email_ok:
            errors.append(f"E-mail : {email_msg}")

        if not password:
            errors.append("Le mot de passe est obligatoire.")
        else:
            rules = check_password_rules(password)
            failed = [r for r, ok in rules.items() if not ok]
            if failed:
                errors.append("Mot de passe trop faible — règles non respectées : " + ", ".join(failed))

        if password and password_confirm and password != password_confirm:
            errors.append("Les mots de passe ne correspondent pas.")

        if errors:
            for e in errors:
                st.error(f"❌ {e}")
        else:
            role_map = {
                "Propriétaire d'entrepôt": "owner",
                "Chercheur d'entrepôt":    "researcher",
            }
            db_role = role_map.get(role, "owner")

            parts      = nom.strip().split(" ", 1)
            first_name = parts[0]
            last_name  = parts[1] if len(parts) > 1 else ""

            from core.auth import create_user
            success = create_user(db_role, first_name, last_name, email, password)
            if success:
                st.success("✅ Compte créé avec succès !")
                st.info("Vous pouvez maintenant vous connecter.")
            else:
                st.error("❌ Adresse e-mail déjà utilisée ou problème serveur.")

    st.markdown("---")
    st.caption("Vous avez déjà un compte ?")
    if st.button("Se connecter", use_container_width=True):
        st.switch_page("pages/1_Login.py")

    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# Footer
# =====================================================
st.markdown("""
<div class="footer">
    © 2025 OptiStock Logistics Intelligence — Tous droits réservés<br/>
    <a href="#">Politique de confidentialité</a> •
    <a href="#">Conditions d'utilisation</a> •
    <a href="#">Support</a>
</div>
""", unsafe_allow_html=True)
