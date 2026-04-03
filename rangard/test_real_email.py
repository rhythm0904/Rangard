#!/usr/bin/env python3
"""Test email to real address: rhythmbhatnagar.cse22@jimsgn.org"""
import sys
sys.path.insert(0, '.')

from app.services.email import get_email_service

print("=" * 70)
print("SEND EMAILS TO: rhythmbhatnagar.cse22@jimsgn.org")
print("=" * 70)

email_svc = get_email_service()

print("\n1️⃣  SENDING VERIFICATION EMAIL...")
success, error = email_svc.send_email_verification(
    to_email='rhythmbhatnagar.cse22@jimsgn.org',
    verification_link='https://rangard.app/verify?token=test123abc'
)

if success:
    print("✅ Verification email sent!")
else:
    print(f"❌ Failed: {error}")
    sys.exit(1)

print("\n2️⃣  SENDING THREAT ALERT EMAIL...")
success, error = email_svc.send_threat_alert(
    to_email='rhythmbhatnagar.cse22@jimsgn.org',
    to_name='Rhythm Bhatnagar',
    filename='suspicious_file.exe',
    threat_level='HIGH',
    confidence=0.95,
    patterns=['Encryption routine', 'File locking detected'],
    scan_id='scan-real-001'
)

if success:
    print("✅ Threat alert email sent!")
else:
    print(f"❌ Failed: {error}")
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ BOTH EMAILS SENT SUCCESSFULLY!")
print("=" * 70)
print("""
📧 2 Emails should arrive at: rhythmbhatnagar.cse22@jimsgn.org

1. Verification Email
   - Subject: "Verify Your Email - RANGARD"
   - Contains: Verification button and link
   
2. Threat Alert Email
   - Subject: "[RANGARD] HIGH Threat Detected"
   - Contains: Threat details and scan information

⏰ Delivery: Usually arrives in 1-5 seconds
📍 Check: Inbox, Spam, and All Mail folders
""")
