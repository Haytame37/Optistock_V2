import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

def test_email():
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    to_email = sender_email # S'envoyer un mail à soi-même

    print(f"Tentative d'envoi de test...")
    print(f"Serveur: {smtp_server}:{smtp_port}")
    print(f"Expéditeur: {sender_email}")

    msg = MIMEText("Ceci est un test de connexion SMTP pour OptiStock.")
    msg['Subject'] = "Test OptiStock SMTP"
    msg['From'] = sender_email
    msg['To'] = to_email

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.set_debuglevel(1) # Pour voir les détails de la conversation SMTP
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        print("\n✅ TEST RÉUSSI : L'email a été envoyé !")
    except Exception as e:
        print(f"\n❌ TEST ÉCHOUÉ : {e}")

if __name__ == "__main__":
    test_email()
