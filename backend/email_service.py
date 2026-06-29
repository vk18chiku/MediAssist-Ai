# backend/email_service.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Resend HTTP API Configuration
RESEND_API_KEY = os.getenv("SMTP_PASSWORD")  # Your Resend API key (re_...)
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "onboarding@resend.dev")

def send_real_email(to_email, subject, body):
    if not RESEND_API_KEY:
        print("❌ RESEND API KEY missing. Please set SMTP_PASSWORD env variable.")
        return False

    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "from": f"MediAssist AI <{SENDER_EMAIL}>",
                "to": [to_email],
                "subject": subject,
                "text": body
            },
            timeout=10
        )

        if response.status_code == 200:
            print(f"✅ Email sent successfully to {to_email}")
            return True
        else:
            print(f"❌ Resend API error ({response.status_code}): {response.text}")
            return False
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False