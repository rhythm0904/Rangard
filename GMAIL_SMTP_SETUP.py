#!/usr/bin/env python3
"""
RANGARD - Gmail SMTP Setup Guide
═════════════════════════════════════════════════════════════════════════

We've switched from SendGrid to Gmail SMTP for more reliable email delivery.
Gmail is free, simple, and doesn't have the API authentication issues we had.

SETUP STEPS:
═════════════════════════════════════════════════════════════════════════

STEP 1: Enable 2-Factor Authentication on Gmail (if not already done)
  → Go to: https://myaccount.google.com/security
  → Click "2-Step Verification"
  → Follow the setup process
  → This is required for app passwords

STEP 2: Generate Gmail App Password
  → Go to: https://myaccount.google.com/apppasswords
  → Sign in if prompted
  → Select Device: "Windows Computer" (or your device)
  → Select App: "Mail"
  → Click "Generate"
  → Google will show a 16-character password (example: abcd efgh ijkl mnop)
  → Copy this password (remove spaces if any)

STEP 3: Update .env File
  → Edit: rangard/.env
  → Find: GMAIL_APP_PASSWORD=your_16_char_app_password_here
  → Replace with your 16-character password from step 2
  → Example: GMAIL_APP_PASSWORD=abcdefghijklmnop
  → Save file

STEP 4: Test Email Sending
  → Run: python rangard/test_gmail_smtp.py
  → Should show: "✅ EMAIL SENT SUCCESSFULLY!"

STEP 5: Restart Server
  → Kill running server (Ctrl+C)
  → Run: python rangard/run.py
  → Server will now send emails via Gmail

═════════════════════════════════════════════════════════════════════════

WHAT IS AN APP PASSWORD?

An "app password" is a 16-character code that Gmail generates for third-party
applications. It's MORE SECURE than using your regular Gmail password because:

  ✓ It can only be used for SMTP (not to access Gmail directly)
  ✓ You can revoke it anytime
  ✓ Access is limited to the "Mail" app only
  ✓ Doesn't expose your main Gmail password

═════════════════════════════════════════════════════════════════════════

CURRENT CONFIGURATION:

Email Sender:          rangard.safe@gmail.com
SMTP Server:           smtp.gmail.com
SMTP Port:             587 (TLS Secure)
Connection Type:       TLS (Secure)
Sender Verification:   ✅ ALREADY VERIFIED IN SENDGRID
App Password Status:   ⏳ WAITING FOR YOU TO GENERATE

═════════════════════════════════════════════════════════════════════════

EMAIL WORKFLOW AFTER SETUP:

1. User Registers
   ↓
2. System sends verification email via Gmail SMTP
   ↓
3. User verifies email
   ↓
4. User uploads suspicious file
   ↓
5. Threat detected → Email alert sent via Gmail SMTP
   ↓
6. User receives alert in inbox with details

═════════════════════════════════════════════════════════════════════════

TROUBLESHOOTING:

Problem: "Gmail authentication failed"
  → Check app password is exactly 16 characters
  → Remove any spaces from the password
  → Verify 2-factor authentication is enabled
  → Verify you selected "Mail" and not "Google Drive" or other apps

Problem: "Connection refused"
  → Gmail SMTP might be blocked by firewall
  → Port 587 should be open (Google's TLS port)
  → Try with corporate VPN/proxy if on restrictive network

Problem: "Email not received"
  → Check spam folder
  → Verify recipient email is correct
  → Check Gmail sent folder (emails DO go there)
  → Wait 5-10 seconds (sometimes delayed)

═════════════════════════════════════════════════════════════════════════

Once you generate the app password and update .env:

1. Run: python rangard/test_gmail_smtp.py
2. Watch for: "✅ EMAIL SENT SUCCESSFULLY!"
3. Restart server
4. System will send verification and alert emails automatically

═════════════════════════════════════════════════════════════════════════
"""

if __name__ == "__main__":
    print(__doc__)
