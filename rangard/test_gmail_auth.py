#!/usr/bin/env python3
"""Test Gmail SMTP authentication."""
import smtplib
import sys
sys.path.insert(0, '.')

from app.core.config import get_settings

settings = get_settings()
gmail_user = settings.EMAIL_FROM
gmail_password = settings.GMAIL_APP_PASSWORD

print(f"Email: {gmail_user}", flush=True)
print(f"Password: {'SET' if gmail_password else 'NOT SET'}", flush=True)

try:
    print("\nConnecting to SMTP...", flush=True)
    with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as server:
        print("✓ Connected", flush=True)
        
        print("Starting TLS...", flush=True)
        server.starttls()
        print("✓ TLS started", flush=True)
        
        print(f"Logging in as {gmail_user}...", flush=True)
        server.login(gmail_user, gmail_password)
        print("✓ Authenticated!", flush=True)
        
        print("\n✅ SUCCESS! Authentication works!")
        
except smtplib.SMTPAuthenticationError as e:
    print(f"\n❌ Authentication failed: {e}", flush=True)
    print("Possible issues:", flush=True)
    print("  • App password is incorrect", flush=True)
    print("  • 2-Factor Authentication not enabled", flush=True)
    print("  • Account has specific security restrictions", flush=True)
except Exception as e:
    print(f"\n❌ Error: {e}", flush=True)
    import traceback
    traceback.print_exc()
