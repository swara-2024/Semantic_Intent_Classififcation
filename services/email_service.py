from dotenv import load_dotenv
load_dotenv()

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")



def send_email(to_email: str, subject: str, body: str) -> bool:
    """
    Production SMTP sender
    Uses env vars for credentials
    """

    if not SMTP_USER or not SMTP_PASS:
        print(" EMAIL CONFIG MISSING — set SMTP_USER and SMTP_PASS")
        return False

    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()

        print(" Email sent →", to_email)
        return True

    except Exception as e:
        print(" Email error:", e)
        return False
