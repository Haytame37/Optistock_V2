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

        # =====================================================
        # Logique par étape
        # =====================================================
        if "forgot_step" not in st.session_state:
            st.session_state.forgot_step = "email"

        if st.session_state.forgot_step == "email":
            recovery_email = st.text_input(
                "📧 Votre adresse e-mail",
                placeholder="nom@entreprise.com",
                key="recovery_email_input"
            )

            col_send, col_back = st.columns([2, 1])
            with col_send:
                send_btn = st.button(
                    "✉️ Envoyer l'OTP",
                    type="primary",
                    use_container_width=True,
                    key="send_otp_btn"
                )
            with col_back:
                if st.button("← Retour", use_container_width=True, key="back_btn"):
                    st.switch_page("pages/1_Login.py")

            if send_btn:
                if not recovery_email or "@" not in recovery_email:
                    st.error("❌ Veuillez entrer une adresse e-mail valide.")
                else:
                    conn = sqlite3.connect(DB_PATH)
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT user_id, first_name FROM users WHERE email = ? AND is_active = 1",
                        (recovery_email,)
                    )
                    user = cursor.fetchone()

                    if not user:
                        st.warning("⚠️ Aucun compte actif trouvé avec cette adresse e-mail.")
                        conn.close()
                    else:
                        # Générer un OTP à 6 chiffres
                        otp_code = "".join(secrets.choice(string.digits) for _ in range(6))
                        from utils.helpers import get_current_time
                        from datetime import timedelta
                        
                        expiry_time = (get_current_time() + timedelta(minutes=10)).strftime('%Y-%m-%d %H:%M:%S')
                        
                        # Mettre à jour l'utilisateur avec l'OTP
                        cursor.execute(
                            "UPDATE users SET otp_code = ?, otp_expiry = ? WHERE email = ? AND is_active = 1",
                            (otp_code, expiry_time, recovery_email)
                        )
                        conn.commit()
                        conn.close()

                        first_name = user[1]
                        
                        # Configuration SMTP
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
                              <p style="color:#64748b;font-size:13px;margin:4px 0 0;">Vérification de sécurité</p>
                            </div>
                            <p style="color:#1e293b;font-size:15px;">Bonjour <b>{first_name}</b>,</p>
                            <p style="color:#475569;font-size:14px;line-height:1.6;">
                              Utilisez le code suivant pour réinitialiser votre mot de passe OptiStock :
                            </p>
                            <div style="background:#f0fdf4;border:1px solid #86efac;border-radius:12px;
                                        padding:20px;text-align:center;margin:20px 0;">
                              <div style="font-size:32px;font-weight:900;color:#15803d;
                                          letter-spacing:8px;background:#fff;border-radius:8px;
                                          padding:12px;border:1px dashed #4ade80;">{otp_code}</div>
                              <p style="color:#6b7280;font-size:12px;margin:10px 0 0;">
                                Ce code expirera dans 10 minutes.
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
                            msg["Subject"] = f"🔑 {otp_code} est votre code de vérification OptiStock"
                            msg["From"]    = sender_email
                            msg["To"]      = recovery_email
                            msg.attach(MIMEText(email_html, "html", "utf-8"))

                            with smtplib.SMTP(smtp_server, smtp_port) as server:
                                server.ehlo()
                                server.starttls()
                                server.login(sender_email, sender_pwd)
                                server.sendmail(sender_email, recovery_email, msg.as_string())

                            st.session_state.forgot_step = "otp"
                            st.session_state.reset_email = recovery_email
                            st.success("✅ Code envoyé ! Vérifiez votre boîte mail.")
                            st.rerun()

                        except Exception as ex:
                            st.error(f"❌ Erreur lors de l'envoi de l'email : {ex}")

        elif st.session_state.forgot_step == "otp":
            st.info(f"Un code a été envoyé à **{st.session_state.reset_email}**")
            otp_input = st.text_input("🔢 Entrez le code à 6 chiffres", placeholder="000000", max_chars=6)
            
            col_verify, col_cancel = st.columns([2, 1])
            with col_verify:
                if st.button("Vérifier le code", type="primary", use_container_width=True):
                    if not otp_input:
                        st.error("Veuillez entrer le code.")
                    else:
                        conn = sqlite3.connect(DB_PATH)
                        cursor = conn.cursor()
                        from utils.helpers import get_current_time
                        now = get_current_time().strftime('%Y-%m-%d %H:%M:%S')
                        
                        cursor.execute(
                            "SELECT user_id FROM users WHERE email = ? AND otp_code = ? AND otp_expiry > ?",
                            (st.session_state.reset_email, otp_input, now)
                        )
                        result = cursor.fetchone()
                        conn.close()
                        
                        if result:
                            st.session_state.forgot_step = "reset"
                            st.rerun()
                        else:
                            st.error("❌ Code invalide ou expiré.")
            
            with col_cancel:
                if st.button("Annuler", use_container_width=True):
                    st.session_state.forgot_step = "email"
                    st.rerun()

        elif st.session_state.forgot_step == "reset":
            st.success("✅ Code vérifié. Choisissez un nouveau mot de passe.")
            new_pwd = st.text_input("🔐 Nouveau mot de passe", type="password")
            confirm_pwd = st.text_input("🔁 Confirmez le mot de passe", type="password")
            
            if st.button("Mettre à jour le mot de passe", type="primary", use_container_width=True):
                if not new_pwd:
                    st.error("Veuillez entrer un mot de passe.")
                elif len(new_pwd) < 8:
                    st.error("Le mot de passe doit contenir au moins 8 caractères.")
                elif new_pwd != confirm_pwd:
                    st.error("Les mots de passe ne correspondent pas.")
                else:
                    new_hash = hash_password(new_pwd)
                    conn = sqlite3.connect(DB_PATH)
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE users SET password_hash = ?, must_change_password = 0, otp_code = NULL, otp_expiry = NULL WHERE email = ?",
                        (new_hash, st.session_state.reset_email)
                    )
                    conn.commit()
                    conn.close()
                    
                    st.session_state.forgot_step = "success"
                    st.rerun()

        elif st.session_state.forgot_step == "success":
            st.balloons()
            st.success("🎉 Votre mot de passe a été mis à jour avec succès !")
            if st.button("→ Aller à la connexion", type="primary", use_container_width=True):
                # Nettoyer l'état
                for key in ["forgot_step", "reset_email"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.switch_page("pages/1_Login.py")

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
