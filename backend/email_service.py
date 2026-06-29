# backend/email_service.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Email API Configuration
# Supports both Brevo (default, works with ANY recipient) and Resend
EMAIL_PROVIDER = os.getenv("EMAIL_PROVIDER", "brevo")  # "brevo" or "resend"
EMAIL_API_KEY = os.getenv("EMAIL_API_KEY", os.getenv("SMTP_PASSWORD", ""))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "uttammahato379@gmail.com")
SENDER_NAME = os.getenv("SENDER_NAME", "MediAssist AI")


def _send_via_brevo(to_email, subject, body):
    """Send email using Brevo (Sendinblue) HTTP API — works with ANY recipient."""
    response = requests.post(
        "https://api.brevo.com/v3/smtp/email",
        headers={
            "api-key": EMAIL_API_KEY,
            "Content-Type": "application/json",
            "accept": "application/json"
        },
        json={
            "sender": {"name": SENDER_NAME, "email": SENDER_EMAIL},
            "to": [{"email": to_email}],
            "subject": subject,
            "textContent": body
        },
        timeout=10
    )
    return response


def _send_via_resend(to_email, subject, body):
    """Send email using Resend HTTP API — only sends to account owner email on free plan."""
    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {EMAIL_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "from": f"{SENDER_NAME} <{SENDER_EMAIL}>",
            "to": [to_email],
            "subject": subject,
            "text": body
        },
        timeout=10
    )
    return response


def send_real_email(to_email, subject, body):
    if not EMAIL_API_KEY:
        print("❌ EMAIL_API_KEY missing. Please set it in environment variables.")
        return False

    try:
        if EMAIL_PROVIDER == "resend":
            response = _send_via_resend(to_email, subject, body)
        else:
            response = _send_via_brevo(to_email, subject, body)

        if response.status_code in [200, 201]:
            print(f"✅ Email sent successfully to {to_email} via {EMAIL_PROVIDER}")
            return True
        else:
            print(f"❌ {EMAIL_PROVIDER} API error ({response.status_code}): {response.text}")
            return False
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False