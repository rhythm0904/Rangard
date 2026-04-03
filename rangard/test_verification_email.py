#!/usr/bin/env python3
"""Test the new verification email template."""
import sys
sys.path.insert(0, '.')

print("Testing new email verification template...", flush=True)

try:
    from app.services.email import EmailService
    
    email_svc = EmailService()
    
    print("Sending verification email with new template...", flush=True)
    success, error = email_svc.send_email_verification(
        to_email="rangard.safe@gmail.com",
        verification_link="https://rangard.app/verify?token=abc123def456"
    )
    
    if success:
        print("\n✅ SUCCESS! Verification email sent!")
        print("The new professional email template is working.")
    else:
        print(f"\n❌ Failed: {error}")
        sys.exit(1)
        
except Exception as e:
    print(f"ERROR: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)
