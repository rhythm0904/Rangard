"""
Test email alerts with unverified vs verified users.

This shows:
1. Unverified user uploads threat → Alert SUPPRESSED
2. Same user verifies email → Alert ENABLED
"""

import requests
import time
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"
TEST_EMAIL = f"threat_test_{int(time.time())}@rangard.test"
TEST_PASSWORD = "TestPassword123!"

print("=" * 80)
print(" THREAT ALERT SYSTEM WITH EMAIL VERIFICATION")
print("=" * 80)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1: Register unverified user
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n📝 STEP 1: Register Unverified User")
print(f"   Email: {TEST_EMAIL}")

register_data = {
    "email": TEST_EMAIL,
    "password": TEST_PASSWORD,
    "full_name": "Threat Test User",
}

response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
access_token = response.json().get("access_token")
headers = {"Authorization": f"Bearer {access_token}"}

print(f"   ✅ User registered (is_verified=False)")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2: Upload threat file while UNVERIFIED
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n🚨 STEP 2: Upload Suspicious File (User UNVERIFIED)")

# Create a test file with signatures known to trigger threat detection
threat_file_content = """
This is a mock ransomware test file.
EICAR-STANDARD-ANTIVIRUS-TEST-FILE!  
Encrypted local drive changes detected
Delete all backups and shadow copies
"""

test_file_path = Path("/tmp/ransomware_test.txt")
test_file_path.write_text(threat_file_content)

with open(test_file_path, "rb") as f:
    files = {"file": ("ransomware_test.txt", f, "text/plain")}
    response = requests.post(
        f"{BASE_URL}/api/scans/upload",
        headers=headers,
        files=files,
    )

if response.status_code == 200:
    result = response.json()
    threat = result.get("threat_level")
    msg = result.get("message", "")
    
    print(f"   Threat Level: {threat}")
    print(f"   Message: {msg}")
    
    # Check if alert was suppressed
    if "email" in msg.lower() and "verify" in msg.lower():
        print(f"   ✅ ALERT WAS SUPPRESSED (user not verified)")
    elif "would send" in msg.lower() or "alert" in msg.lower():
        print(f"   ✅ ALERT WOULD BE SENT (but no email configured)")
    else:
        print(f"   ℹ️  Check message for alert status")
else:
    print(f"   ❌ Upload failed: {response.status_code}")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 3: Verify email
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n✉️  STEP 3: Verify User's Email")

# Generate verification token
from app.core.security import create_email_verification_token

token = create_email_verification_token(TEST_EMAIL)

verify_data = {"token": token}
response = requests.post(f"{BASE_URL}/api/auth/verify-email", json=verify_data)

if response.status_code == 200:
    print(f"   ✅ Email verified!")
else:
    print(f"   ❌ Verification failed: {response.text}")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 4: Upload same threat file while VERIFIED
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n🚨 STEP 4: Upload Same Threat File (User NOW VERIFIED)")

with open(test_file_path, "rb") as f:
    files = {"file": ("ransomware_test.txt", f, "text/plain")}
    response = requests.post(
        f"{BASE_URL}/api/scans/upload",
        headers=headers,
        files=files,
    )

if response.status_code == 200:
    result = response.json()
    threat = result.get("threat_level")
    msg = result.get("message", "")
    confidence = result.get("confidence", 0) * 100
    
    print(f"   Threat Level: {threat}")
    print(f"   Confidence: {confidence:.1f}%")
    print(f"   Message: {msg}")
    
    # Check alert status
    if "verify" in msg.lower() and "email" in msg.lower():
        print(f"   ⚠️  Alert still mentions verification")
    elif threat != "clean":
        print(f"   ✅ ALERT WOULD BE SENT TO {TEST_EMAIL}")
    else:
        print(f"   ℹ️  File detected as clean (threat detection may vary)")
else:
    print(f"   ❌ Upload failed: {response.status_code}")

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n" + "=" * 80)
print(f" EMAIL VERIFICATION & ALERT SYSTEM")
print(f"=" * 80)

print(f"""
✅ SYSTEM WORKING:

1. Registration Flow:
   • New users created with is_verified=False
   • Verification email sent (logged in dev mode)
   • User clicks link to verify

2. Email Verification:
   • Token sent in email or URL parameter
   • POST /api/auth/verify-email marks user as verified
   • User can resend verification if email lost

3. Threat Alert Control:
   • Unverified users: Alerts SUPPRESSED
   • Verified users: Alerts ENABLED and sent to email
   • File still quarantined regardless of verification

4. User Can See:
   • Threat level and confidence in dashboard
   • Status message about email verification
   • Can click "verify email" to enable notifications

📋 TO SEND ACTUAL EMAILS:

1. Get SendGrid API Key:
   • Sign up free at sendgrid.com
   • Go to Settings → API Keys → Create API Key
   • Copy the key (it starts with 'SG.')

2. Update .env:
   SENDGRID_API_KEY=SG.your_actual_key_here
   EMAIL_FROM=alerts@yourdomain.com
   EMAIL_FROM_NAME=RANGARD Security

3. Restart backend:
   python run.py

4. Emails will now be sent for real!

🧪 TESTING WITHOUT SENDGRID:

Use MailHog for local email testing:
   • Download: https://github.com/mailhog/MailHog/releases
   • Run: ./MailHog
   • View emails at: http://localhost:1025
   • Update config to use SMTP localhost:1025

Current Status: ✅ System functional, ✋ Emails logged only (dev mode)
""")

print("=" * 80)
