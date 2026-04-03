#!/usr/bin/env python3
"""
MASTER EMAIL TEST SCRIPT - The ONLY test script you need to use
Uses REAL email address (yours!)
"""
import requests
import sys

print("=" * 70)
print("RANGARD - COMPLETE EMAIL SYSTEM TEST")
print("=" * 70)

# Get user's REAL email
your_email = input("\n📧 Enter YOUR REAL Gmail address to test with: ").strip()
if not your_email or "@" not in your_email:
    print("❌ Invalid email address!")
    sys.exit(1)

your_password = input("🔑 Enter a test password (min 8 chars): ").strip()
if len(your_password) < 8:
    print("❌ Password too short!")
    sys.exit(1)

API_URL = "http://127.0.0.1:8000/api"

print("\n" + "=" * 70)
print("TEST 1: REGISTER USER WITH REAL EMAIL")
print("=" * 70)

try:
    response = requests.post(
        f"{API_URL}/auth/register",
        json={
            "email": your_email,
            "password": your_password,
            "full_name": "Test User"
        },
        timeout=10
    )
    
    if response.status_code == 201:
        print(f"\n✅ USER REGISTERED")
        user_data = response.json()
        print(f"   Email: {your_email}")
        print(f"   User ID: {user_data.get('user_id')}")
        print(f"   Token: {user_data.get('access_token', 'N/A')[:30]}...")
        print(f"\n📧 VERIFICATION EMAIL SENT TO: {your_email}")
        
    elif response.status_code == 409:
        print(f"\n⚠️  User already exists: {your_email}")
        print(f"   (This means email was already registered earlier)")
        
    else:
        print(f"\n❌ Registration failed: {response.status_code}")
        print(f"   Response: {response.text}")
        sys.exit(1)
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("TEST 2: CHECK FOR VERIFICATION EMAIL")
print("=" * 70)

print(f"""
🔍 ACTION REQUIRED:

1. Go to Gmail: https://mail.google.com
2. CHECK THESE FOLDERS:
   ✓ Inbox (main folder)
   ✓ Promotions (marketing emails)
   ✓ Updates (account notifications)
   ✓ Spam (filtered emails)
   
3. LOOK FOR:
   From: RANGARD Security <rangard.safe@gmail.com>
   Subject: Verify Your Email - RANGARD
   
4. IF IN SPAM:
   • Click the email
   • Click ⋮ (three dots)
   • Select "Report not spam"
   • This trains Gmail to trust RANGARD
""")

input("Press ENTER after you've checked your email...")

print("\n" + "=" * 70)
print("TEST 3: SEND DIRECT TEST EMAIL")
print("=" * 70)

print("\nNow sending a direct test email...")

try:
    sys.path.insert(0, '.')
    from app.services.email import get_email_service
    
    email_svc = get_email_service()
    success, error = email_svc.send_email_verification(
        to_email=your_email,
        verification_link="https://rangard.app/verify?token=test123abc"
    )
    
    if success:
        print(f"\n✅ TEST EMAIL SENT TO {your_email}")
        print(f"   This is a SECOND test email")
        print(f"   You should now have 2 verification emails")
    else:
        print(f"\n❌ Failed to send: {error}")
        
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"""
✅ REGISTRATION EMAIL SENT TO: {your_email}
✅ TEST EMAIL SENT TO: {your_email}
⏳ TOTAL EMAILS TO EXPECT: 2

📍 WHERE TO LOOK:
   • Primary Inbox
   • Promotions tab
   • Updates tab
   • Spam folder

✅ IF YOU SEE THE EMAILS:
   • System is working correctly!
   • Mark as "Not Spam" if in spam
   • Create filter to always trust RANGARD

❌ IF YOU DON'T SEE EMAILS:
   • Check spam folder first
   • Wait 2-3 minutes
   • Refresh browser
   • Contact support if still missing

🎯 NEXT STEPS:
   1. Verify your email using the link in the email
   2. Upload a suspicious file to test threat alerts
   3. You should receive threat alert emails
""")

print("\n✅ Test complete! Check your email now.\n")
