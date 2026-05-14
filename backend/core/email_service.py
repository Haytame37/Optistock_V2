import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

def send_email(to_email: str, subject: str, html_content: str):
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print(f"[SIMULATION EMAIL] Vers: {to_email} | Sujet: {subject}")
        # print(f"Contenu: {html_content}")
        return True

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"OptiStock Solutions <{SENDER_EMAIL}>"
    msg["To"] = to_email
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"❌ Erreur envoi email: {e}")
        return False

def send_otp_email(to_email: str, first_name: str, otp_code: str):
    subject = f"🔑 {otp_code} est votre code de vérification OptiStock"
    html = f"""
    <html><body style="font-family:sans-serif;background:#f4fafd;padding:20px;">
      <div style="max-width:400px;margin:auto;background:#fff;border-radius:12px;padding:20px;border:1px solid #dbe7f3;">
        <h2 style="color:#005da7;text-align:center;">OptiStock Solutions</h2>
        <p>Bonjour <b>{first_name}</b>,</p>
        <p>Utilisez le code suivant pour réinitialiser votre mot de passe :</p>
        <div style="background:#f0fdf4;padding:15px;text-align:center;font-size:24px;font-weight:bold;letter-spacing:5px;color:#15803d;border:1px dashed #4ade80;">
          {otp_code}
        </div>
        <p style="font-size:12px;color:#64748b;text-align:center;margin-top:15px;">Ce code expirera dans 10 minutes.</p>
      </div>
    </body></html>
    """
    return send_email(to_email, subject, html)
