import streamlit as st
import sqlite3
import secrets
import string
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from utils.ui import hide_sidebar
from utils.db import DB_PATH
from core.auth import hash_password

load_dotenv()

# =====================================================
# Configuration de la page
# =====================================================
st.set_page_config(
    page_title="OptiStock – Mot de passe oublié",
    page_icon="🔑",
    layout="wide"
)
hide_sidebar()

# =====================================================
# CSS
# =====================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Work+Sans:wght@800;900&display=swap');

body { font-family: Inter, sans-serif; background-color: #f4fafd; }

.header {
    position: fixed; top: 0; left: 0; width: 100%;
    background: rgba(255,255,255,0.9); backdrop-filter: blur(6px);
    border-bottom: 1px solid #dbe7f3; padding: 16px;
    display: flex; justify-content: center; z-index: 999;
}
.brand {
    font-family: 'Work Sans', sans-serif; font-weight: 900;
    font-size: 24px; color: #005da7;
}
.footer {
    margin-top: 48px; padding: 24px; border-top: 1px solid #e1e5ea;
    text-align: center; font-size: 13px; color: #6b7280;
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

st.markdown("<div style='height:90px'></div>", unsafe_allow_html=True)

# =====================================================
# Formulaire centré
# =====================================================
_, col_form, _ = st.columns([1, 1.4, 1])

with col_form:
    with st.container(border=True):
        st.markdown("## 🔑 Mot de passe oublié")
        st.caption("Récupérez l'accès à votre compte OptiStock")
        st.write("")

        recovery_email = st.text_input(
            "📧 Votre adresse e-mail",
            placeholder="nom@entreprise.com",
            key="recovery_email"
        )

        col_send, col_back = st.columns([2, 1])
        with col_send:
            send_btn = st.button(
                "✉️ Envoyer le mot de passe",
                type="primary",
                use_container_width=True,
                key="send_btn"
            )
        with col_back:
            if st.button("← Retour", use_container_width=True, key="back_btn"):
                st.switch_page("pages/1_Login.py")

        st.write("")

        if send_btn:
            if not recovery_email or "@" not in recovery_email:
                st.error("❌ Veuillez entrer une adresse e-mail valide.")
            else:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT user_id, first_name, role FROM users WHERE email = ? AND is_active = 1",
                    (recovery_email,)
                )
                accounts = cursor.fetchall()

                if not accounts:
                    st.warning("⚠️ Aucun compte actif trouvé avec cette adresse e-mail.")
                    conn.close()
                else:
                    # Générer un mot de passe temporaire sécurisé
                    alphabet = string.ascii_letters + string.digits + "!@#$%"
                    temp_pwd = (
                        secrets.choice(string.ascii_uppercase) +
                        secrets.choice(string.ascii_lowercase) +
                        secrets.choice(string.digits) +
                        secrets.choice("!@#$%") +
                        "".join(secrets.choice(alphabet) for _ in range(6))
                    )

                    # Mettre à jour tous les comptes + activer le flag de réinitialisation
                    new_hash = hash_password(temp_pwd)
                    cursor.execute(
                        "UPDATE users SET password_hash = ?, must_change_password = 1 WHERE email = ? AND is_active = 1",
                        (new_hash, recovery_email)
                    )
                    conn.commit()
                    conn.close()

                    roles_fr = {"admin": "Administrateur", "owner": "Propriétaire", "researcher": "Chercheur"}
                    comptes_str = ", ".join(
                        f"{row[1]} ({roles_fr.get(row[2], row[2])})"
                        for row in accounts
                    )
                    first_name = accounts[0][1]

                    # ── Envoi réel via SMTP Gmail ──────────────────────────────
                    smtp_server  = os.getenv("SMTP_SERVER",   "smtp.gmail.com")
                    smtp_port    = int(os.getenv("SMTP_PORT", "587"))
                    sender_email = os.getenv("SENDER_EMAIL",  "")
                    sender_pwd   = os.getenv("SENDER_PASSWORD", "")

                    email_html = f"""
<html><body style="font-family:Inter,sans-serif;background:#f4fafd;padding:30px;">
  <div style="max-width:480px;margin:auto;background:#fff;border-radius:16px;
              border:1px solid #dbe7f3;padding:32px;box-shadow:0 8px 24px rgba(0,93,167,0.08);">
    <div style="text-align:center;margin-bottom:24px;">
      <h2 style="color:#005da7;margin:0;">📦 OptiStock Solutions</h2>
      <p style="color:#64748b;font-size:13px;margin:4px 0 0;">Réinitialisation de mot de passe</p>
    </div>
    <p style="color:#1e293b;font-size:15px;">Bonjour <b>{first_name}</b>,</p>
    <p style="color:#475569;font-size:14px;line-height:1.6;">
      Vous avez demandé la réinitialisation de votre mot de passe pour :<br>
      <b>{comptes_str}</b>
    </p>
    <div style="background:#f0fdf4;border:1px solid #86efac;border-radius:12px;
                padding:20px;text-align:center;margin:20px 0;">
      <p style="color:#166534;font-size:13px;margin:0 0 8px;">Votre nouveau mot de passe temporaire :</p>
      <div style="font-size:28px;font-weight:900;color:#15803d;
                  letter-spacing:4px;background:#fff;border-radius:8px;
                  padding:12px;border:1px dashed #4ade80;">{temp_pwd}</div>
      <p style="color:#6b7280;font-size:12px;margin:10px 0 0;">
        Connectez-vous avec ce mot de passe et changez-le après connexion.
      </p>
    </div>
    <p style="color:#94a3b8;font-size:12px;text-align:center;margin-top:24px;">
      Si vous n'êtes pas à l'origine de cette demande, ignorez cet email.<br>
      © 2026 OptiStock Logistics Intelligence
    </p>
  </div>
</body></html>"""

                    try:
                        msg = MIMEMultipart("alternative")
                        msg["Subject"] = "🔑 OptiStock — Votre nouveau mot de passe temporaire"
                        msg["From"]    = sender_email
                        msg["To"]      = recovery_email
                        msg.attach(MIMEText(email_html, "html", "utf-8"))

                        with smtplib.SMTP(smtp_server, smtp_port) as server:
                            server.ehlo()
                            server.starttls()
                            server.login(sender_email, sender_pwd)
                            server.sendmail(sender_email, recovery_email, msg.as_string())

                        st.success("✅ Email envoyé avec succès !")
                        st.info(f"📧 Un email contenant votre nouveau mot de passe a été envoyé à **{recovery_email}**. Vérifiez votre boîte de réception (et les spams si nécessaire).")

                        st.write("")
                        if st.button("→ Aller à la connexion", type="primary", use_container_width=True, key="goto_login"):
                            st.switch_page("pages/1_Login.py")

                    except smtplib.SMTPAuthenticationError:
                        st.error("❌ Erreur d'authentification SMTP. Vérifiez les identifiants dans le fichier .env")
                    except smtplib.SMTPException as smtp_err:
                        st.error(f"❌ Erreur d'envoi email : {smtp_err}")
                    except Exception as ex:
                        st.error(f"❌ Erreur inattendue : {ex}")

        st.markdown("---")
        st.caption("Vous vous souvenez de votre mot de passe ?")
        if st.button("Se connecter", use_container_width=True, key="login_link"):
            st.switch_page("pages/1_Login.py")

# =====================================================
# Footer
# =====================================================
st.markdown("""
<div class="footer">
    © 2026 OptiStock Logistics Intelligence — Tous droits réservés<br>
    <a href="#">Politique de confidentialité</a> •
    <a href="#">Conditions d'utilisation</a> •
    <a href="#">Support</a>
</div>
""", unsafe_allow_html=True)
