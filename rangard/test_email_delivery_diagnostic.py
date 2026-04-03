#!/usr/bin/env python3
"""
Test email delivery and help diagnose mail delivery issues.

This script will help you:
1. Send test emails to YOUR Gmail inbox
2. Know exactly where to look for the emails
3. Identify if emails are in spam/junk
"""
import sys
sys.path.insert(0, '.')

from app.services.email import EmailService

print("=" * 70)
print("EMAIL DELIVERY DIAGNOSTIC TEST")
print("=" * 70)

# Use your personal Gmail inbox
YOUR_EMAIL = input("\n📧 Enter YOUR Gmail address to receive test emails: ").strip()

if not YOUR_EMAIL or "@" not in YOUR_EMAIL:
    print("❌ Invalid email address!")
    sys.exit(1)

print(f"\n✓ Test email will be sent to: {YOUR_EMAIL}")
print(f"✓ Sender will be: rangard.safe@gmail.com")

try:
    email_svc = EmailService()
    
    print("\n" + "-" * 70)
    print("SENDING TEST VERIFICATION EMAIL...")
    print("-" * 70)
    
    success, error = email_svc.send_email_verification(
        to_email=YOUR_EMAIL,
        verification_link="https://rangard.app/verify?token=test123abc"
    )
    
    if success:
        print("\n✅ EMAIL SENT SUCCESSFULLY!")
        print("\n" + "=" * 70)
        print("WHAT TO CHECK NOW")
        print("=" * 70)
        print("\n1️⃣  CHECK YOUR INBOX")
        print(f"   Go to your Gmail inbox at: https://mail.google.com")
        print(f"   Look for an email from: RANGARD Security <rangard.safe@gmail.com>")
        print(f"   Subject: 'Verify Your Email - RANGARD'")
        
        print("\n2️⃣  CHECK OTHER FOLDERS")
        print("   If not in Inbox, check:")
        print("   • Spam folder (Promotions)")
        print("   • Updates folder")
        print("   • All Mail folder")
        
        print("\n3️⃣  MARK AS NOT SPAM")
        print("   If found in Spam:")
        print("   • Click the email")
        print("   • Click 'Report not spam' button")
        print("   • This tells Gmail to deliver future emails normally")
        
        print("\n4️⃣  VERIFY EMAIL HEADERS")
        print("   In the email:")
        print("   • Click the 3 dots menu (⋮)")
        print("   • Select 'Show original'")
        print("   • Check these headers exist:")
        print("      - From: RANGARD Security <rangard.safe@gmail.com>")
        print("      - To: " + YOUR_EMAIL)
        print("      - Date: [current date/time]")
        
        print("\n" + "=" * 70)
        print("EMAIL DELIVERY LOGS")
        print("=" * 70)
        print("\nSystem sent email with:")
        print(f"  • From: rangard.safe@gmail.com")
        print(f"  • To: {YOUR_EMAIL}")
        print(f"  • Subject: Verify Your Email - RANGARD")
        print(f"  • Content: Professional verification email")
        print(f"  • Headers: Complete MIME headers added")
        
        print("\n" + "=" * 70)
        print("If you still don't see the email after 2-3 minutes:")
        print("=" * 70)
        print("\n⚠️  POSSIBLE ISSUES:")
        print("   1. Gmail spam filters are blocking it")
        print("   2. Email address is incorrect")
        print("   3. Email is in a filtered label")
        print("\n✅ SOLUTION:")
        print("   1. Check spam/promotions folders")
        print("   2. Mark as 'Not Spam' if found")
        print("   3. Contact support if still having issues")
        
    else:
        print(f"\n❌ EMAIL SEND FAILED")
        print(f"   Error: {error}")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
