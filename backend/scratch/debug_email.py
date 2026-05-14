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

print(f"DEBUG: FROM={SENDER_EMAIL} HOST={SMTP_SERVER}:{SMTP_PORT}")

msg = MIMEMultipart("alternative")
msg["Subject"] = "Test Debug"
msg["From"] = SENDER_EMAIL
msg["To"] = SENDER_EMAIL
msg.attach(MIMEText("Test content", "plain"))

try:
    print("Connecting...")
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.set_debuglevel(1)
    server.starttls()
    print("Logging in...")
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    print("Sending...")
    server.sendmail(SENDER_EMAIL, SENDER_EMAIL, msg.as_string())
    server.quit()
    print("SUCCESS")
except Exception as e:
    print(f"FAILED: {e}")
