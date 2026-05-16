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
def send_iot_alert_email(to_email, warehouse_name, product_name, temp, hum):
    """
    Envoie un email d'alerte critique suite à un dépassement de seuil IoT prolongé.
    """
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")

    if not sender_email or not sender_password:
        print(f"[SIMULATION] Email Alert: {to_email}")
        return False

    subject = f"ALERTE CRITIQUE : Seuil depasse - {warehouse_name}"
    body = f"""
    ALERTE CRITIQUE DE SECURITE
    
    L'entrepôt '{warehouse_name}' a depasse les seuils pour le produit : {product_name}.
    
    DETAILS :
    - Temperature : {temp} C
    - Humidite : {hum} %
    
    Action immediate requise.
    
    OptiStock IoT Sentinel.
    """
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = f"OptiStock IoT <{sender_email}>"
    msg['To'] = to_email

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        print(f"✅ Email d'alerte IoT envoyé avec succès à {to_email}")
        return True
    except Exception as e:
        print(f"❌ ERREUR SMTP ALERTE : {str(e)}")
        return False

def send_offer_received_email(to_email, owner_name, warehouse_name):
    """
    Informe le chercheur qu'il a reçu une offre de location.
    """
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")

    if not sender_email or not sender_password:
        print(f"[SIMULATION] Offre reçue par: {to_email} de {owner_name}")
        return False

    msg = MIMEMultipart()
    msg['From'] = f"OptiStock Solutions <{sender_email}>"
    msg['To'] = to_email
    msg['Subject'] = "📩 Nouvelle offre de location reçue !"

    body = f"""
    Bonjour,
    
    Bonne nouvelle ! Le propriétaire {owner_name} vient de vous envoyer une offre formelle pour l'entrepôt : {warehouse_name}.
    
    Vous pouvez dès à présent consulter les détails de cette offre dans votre messagerie OptiStock. Une fois l'offre acceptée, vos accès au monitoring IoT seront instantanément activés.
    
    L'équipe OptiStock.
    """
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        return True
    except Exception:
        return False

def send_acceptance_confirmation_email(to_email, researcher_name, warehouse_name):
    """
    Informe le propriétaire que son offre a été acceptée.
    """
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")

    if not sender_email or not sender_password:
        print(f"[SIMULATION] Offre acceptée pour: {to_email} par {researcher_name}")
        return False

    msg = MIMEMultipart()
    msg['From'] = f"OptiStock Solutions <{sender_email}>"
    msg['To'] = to_email
    msg['Subject'] = "✅ Votre offre a été acceptée !"

    body = f"""
    Bonjour,
    
    Félicitations ! Le chercheur {researcher_name} a accepté votre offre de location pour l'entrepôt : {warehouse_name}.
    
    La transaction est désormais finalisée. Les capteurs IoT ont été activés pour le locataire et l'entrepôt est officiellement marqué comme loué.
    
    L'équipe OptiStock.
    """
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        return True
    except Exception:
        return False
