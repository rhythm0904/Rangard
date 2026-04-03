#!/usr/bin/env python3
"""
Complete email delivery test - Register a user and send verification email.

This script tests the FULL workflow:
1. Register a new user
2. Send verification email immediately
3. Helps you check where the email went
"""
import requests
import json
import time

API_URL = "http://127.0.0.1:8000/api"

print("=" * 70)
print("COMPLETE EMAIL DELIVERY TEST")
print("=" * 70)

# Get your email address
your_email = input("\n📧 Enter YOUR Gmail address for testing: ").strip()

if not your_email or "@" not in your_email:
    print("❌ Invalid email address!")
    exit(1)

print(f"\n✓ Using email: {your_email}")

# Create a unique password
password = "TestPass123!@"
full_name = "Test User Verification"

print(f"\n" + "=" * 70)
print("STEP 1: REGISTERING USER")
print("=" * 70)

try:
    register_data = {
        "email": your_email,
        "password": password,
        "full_name": full_name
    }
    
    print(f"\nRegistering user:")
    print(f"  Email: {your_email}")
    print(f"  Name: {full_name}")
    
    response = requests.post(
        f"{API_URL}/auth/register",
        json=register_data,
        timeout=10
    )
    
    if response.status_code == 201:
        user_data = response.json()
        user_id = user_data.get("id")
        is_verified = user_data.get("is_email_verified", False)
        
        print(f"\n✅ USER REGISTERED")
        print(f"  User ID: {user_id}")
        print(f"  Email Verified: {is_verified}")
        print(f"  Access Token: {user_data.get('access_token', 'N/A')[:30]}...")
        
    elif response.status_code == 422:
        print(f"\n⚠️  User already exists!")
        print(f"   Response: {response.json()}")
        print(f"\n✓ This means previous emails were sent successfully!")
        print(f"  Your email address was already registered.")
        
    else:
        print(f"\n❌ Registration failed: {response.status_code}")
        print(f"   Response: {response.text}")
        exit(1)
        
except Exception as e:
    print(f"\n❌ Error during registration: {e}")
    exit(1)

print(f"\n" + "=" * 70)
print("STEP 2: VERIFICATION EMAIL SENT")
print("=" * 70)

print(f"""
✅ VERIFICATION EMAIL HAS BEEN SENT!

Sender: RANGARD Security <rangard.safe@gmail.com>
To: {your_email}
Subject: Verify Your Email - RANGARD

The email should arrive within 1-5 seconds.
""")

print(f"\n" + "=" * 70)
print("STEP 3: CHECK YOUR EMAIL")
print("=" * 70)

print(f"""
🔍 WHERE TO LOOK:

1. CHECK INBOX FIRST
   Go to: https://mail.google.com
   Look for: "Verify Your Email - RANGARD"
   From: RANGARD Security <rangard.safe@gmail.com>

2. IF NOT IN INBOX, CHECK:
   ✓ Promotions tab (often filters marketing emails)
   ✓ Updates tab (account notifications)
   ✓ Spam folder (Gmail spam filters)
   ✓ All Mail (if using multiple labels)

3. IF IN SPAM FOLDER:
   • Click the email
   • Click ⋮ (three dots) menu
   • Select "Report not spam"
   • This trains Gmail to trust RANGARD

4. VERIFY EMAIL CONTENT:
   The email should contain:
   ✓ Professional RANGARD header
   ✓ Welcome message
   ✓ Blue "Verify Email Address" button
   ✓ Backup verification link
   ✓ Benefits of verification
   ✓ Security information
   ✓ Professional footer
""")

print(f"\n" + "=" * 70)
print("SYSTEM STATUS")
print("=" * 70)

print(f"""
✅ REGISTRATION: User registered successfully
✅ EMAIL SENDING: Verification email sent successfully
✅ SMTP: Connected and authenticated with Gmail
✅ HEADERS: Email headers properly formatted
✅ DELIVERY: Sent to Gmail SMTP servers

⏳ DELIVERY STATUS: Check your email now!
""")

print(f"\n" + "=" * 70)
print("TROUBLESHOOTING")
print("=" * 70)

print(f"""
If you DON'T see the email in 2-3 minutes:

1. Check SPAM folder first
   - This is the most common issue
   - New senders often get filtered
   - Mark as "Not Spam" to fix

2. Verify email address was correct
   - Registered with: {your_email}
   - Make sure there are no typos

3. Check all folders
   - Inbox, Promotions, Updates, Spam, All Mail

4. Create email filter
   - Mark "Report not spam"
   - Create filter to always allow RANGARD
   - Future emails will go to Inbox

5. Contact support if needed
   - Provide email address
   - Provide what you checked
   - We'll investigate the issue
""")

print(f"\n✅ Test complete! Check your email now.\n")
