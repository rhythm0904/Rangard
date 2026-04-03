#!/usr/bin/env python3
"""Test sending an actual email via Gmail."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
sys.path.insert(0, '.')

from app.core.config import get_settings

settings = get_settings()
gmail_user = settings.EMAIL_FROM
gmail_password = settings.GMAIL_APP_PASSWORD

# Get user's email for testing
your_email = input("📧 Enter YOUR Gmail address to receive test email: ").strip()
if not your_email or "@" not in your_email:
    print("❌ Invalid email address!")
    sys.exit(1)

print(f"Sending test email to: {your_email}", flush=True)
print(f"From: {gmail_user}", flush=True)

try:
    # Create message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "[TEST] RANGARD Email Test"
    msg["From"] = f"RANGARD Security <{gmail_user}>"
    msg["To"] = your_email
    
    text_body = "This is a test email from RANGARD.\n\nIf you see this, email is working!"
    html_body = "<html><body><h1>Test Email</h1><p>This is a test email from RANGARD.</p><p>If you see this, email is working!</p></body></html>"
    
    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))
    
    print("\nConnecting to SMTP...", flush=True)
    with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as server:
        print("✓ Connected", flush=True)
        server.starttls()
        print("✓ TLS secured", flush=True)
        server.login(gmail_user, gmail_password)
        print("✓ Authenticated", flush=True)
        
        print("Sending email...", flush=True)
        server.send_message(msg)
        print("✓ Email sent!", flush=True)
        
    print(f"\n✅ SUCCESS! Email sent successfully to {your_email}")
    print("Check your inbox and spam folder for the test email.")

except Exception as e:
    print(f"\n❌ Error: {e}", flush=True)
    import traceback
    traceback.print_exc()
