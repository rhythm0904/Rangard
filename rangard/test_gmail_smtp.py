#!/usr/bin/env python3
"""Test Gmail SMTP configuration."""
import sys
sys.path.insert(0, '.')

from app.core.config import get_settings
from app.services.email import get_email_service

settings = get_settings()

print("=" * 60)
print("Gmail SMTP Configuration Test")
print("=" * 60)

print("\n1. Configuration Check")
print(f"   EMAIL_FROM: {settings.EMAIL_FROM}")
print(f"   EMAIL_FROM_NAME: {settings.EMAIL_FROM_NAME}")
print(f"   GMAIL_APP_PASSWORD: {'SET' if settings.GMAIL_APP_PASSWORD and settings.GMAIL_APP_PASSWORD != 'your_16_char_app_password_here' else 'NOT SET'}")

if not settings.GMAIL_APP_PASSWORD or settings.GMAIL_APP_PASSWORD == 'your_16_char_app_password_here':
    print("\n❌ GMAIL_APP_PASSWORD not configured in .env")
    print("\nTo set it up:")
    print("  1. Go to: https://myaccount.google.com/apppasswords")
    print("  2. Select Mail → Windows Computer (or your device)")
    print("  3. Generate a 16-character password")
    print("  4. Update .env: GMAIL_APP_PASSWORD=<your_16_char_password>")
    print("  5. Run this test again")
    sys.exit(1)

print("\n2. Initializing Email Service")
email_svc = get_email_service()
print("   ✅ Service initialized")

# Get user's email for testing
your_email = input("\n3. Enter YOUR Gmail address to test: ").strip()
if not your_email or "@" not in your_email:
    print("❌ Invalid email address!")
    sys.exit(1)

print(f"\n4. Sending test email to {your_email}...")
success, error = email_svc.send_email_verification(
    to_email=your_email,
    verification_link="https://rangard.app/verify?token=test123abc"
)

if success:
    print("   ✅ SUCCESS! Email sent via Gmail SMTP")
    print("\n" + "=" * 60)
    print("✅ Gmail SMTP is working!")
    print("=" * 60)
    print(f"\nEmails will now be sent from: rangard.safe@gmail.com")
    print(f"Check {your_email} inbox for the test email")
    print("\nIf not in inbox, check:")
    print("  • Spam/Promotions folders")
    print("  • Mark as 'Not Spam' if found")
else:
    print(f"   ❌ Failed: {error}")
    print("\nCommon issues:")
    print("  • App password is wrong (should be 16 characters)")
    print("  • 2-Factor Authentication not enabled on Gmail")
    print("  • Gmail SMTP port 587 is blocked by firewall")
    sys.exit(1)
