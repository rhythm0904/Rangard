#!/usr/bin/env python3
"""Direct test of email sending."""
import sys
sys.path.insert(0, '.')

print("Starting email test...", flush=True)

# Get real email address from user
your_email = input("📧 Enter YOUR Gmail address to test: ").strip()
if not your_email or "@" not in your_email:
    print("❌ Invalid email address!")
    sys.exit(1)

try:
    print("1. Importing config...", flush=True)
    from app.core.config import get_settings
    print("   ✓ Config imported", flush=True)
    
    settings = get_settings()
    print(f"   EMAIL_FROM: {settings.EMAIL_FROM}", flush=True)
    print(f"   GMAIL_APP_PASSWORD: {'SET' if settings.GMAIL_APP_PASSWORD else 'NOT SET'}", flush=True)
    
    print("2. Importing email service...", flush=True)
    from app.services.email import EmailService
    print("   ✓ EmailService imported", flush=True)
    
    print("3. Creating email service instance...", flush=True)
    email_svc = EmailService()
    print("   ✓ EmailService created", flush=True)
    
    print(f"4. Sending verification email to {your_email}...", flush=True)
    success, error = email_svc.send_email_verification(
        to_email=your_email,
        verification_link="https://rangard.app/verify?token=test123"
    )
    
    if success:
        print("✅ EMAIL SENT SUCCESSFULLY!")
        print(f"\nCheck {your_email} inbox (and spam folder) for the email.")
    else:
        print(f"❌ EMAIL FAILED: {error}")
        
except Exception as e:
    print(f"ERROR: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)
