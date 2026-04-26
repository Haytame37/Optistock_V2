import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

def send_suspension_email(to_email, reason="Inactivité"):
    """
    Envoie un email de suspension réel via SMTP.
    Les identifiants doivent être configurés dans le fichier .env
    """
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")

    # Si les identifiants ne sont pas configurés, on logue simplement
    if not sender_email or not sender_password:
        print(f"[SIMULATION EMAIL] Vers: {to_email} | Sujet: Compte Suspendu | Raison: {reason}")
        return False

    msg = MIMEMultipart()
    msg['From'] = f"OptiStock Solutions <{sender_email}>"
    msg['To'] = to_email
    msg['Subject'] = "⚠️ Suspension de votre compte OptiStock"

    body = f"""
    Bonjour,

    Nous vous informons que votre compte OptiStock a été suspendu pour la raison suivante : {reason}.

    Selon nos règles de sécurité, un compte 'Propriétaire' ou 'Chercheur' doit être actif (ajout d'entrepôt ou de point de livraison) dans les 2 minutes suivant sa création.

    Si vous pensez qu'il s'agit d'une erreur, veuillez contacter l'administrateur.

    L'équipe OptiStock.
    """
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Sécuriser la connexion
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, to_email, text)
        server.quit()
        print(f"✅ Email de suspension envoyé avec succès à {to_email}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi de l'email : {e}")
        return False
