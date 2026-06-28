# backend/email_service.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 👇 YAHAN APNA EMAIL AUR 16-DIGIT APP PASSWORD DALEIN 👇
MY_EMAIL = "uttammahato379@gmail.com"  # Aapka Gmail
MY_PASSWORD = "vwrjbvzxvdlgnjjz"

def send_real_email(to_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = f"MediAssist AI <{MY_EMAIL}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Gmail SMTP Server connect karna
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(MY_EMAIL, MY_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Real Email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False