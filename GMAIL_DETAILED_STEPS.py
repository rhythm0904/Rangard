#!/usr/bin/env python3
"""
Detailed Gmail App Password Generation Guide
═════════════════════════════════════════════════════════════════════════

IF YOU'RE NOT SEEING THE APP PASSWORDS PAGE:

The "App Passwords" option only appears if you have 2-Factor Authentication
enabled. If you don't see it, follow these steps FIRST.

═════════════════════════════════════════════════════════════════════════

PREREQUISITE: Enable 2-Factor Authentication
═════════════════════════════════════════════════════════════════════════

Step 1: Go to Google Account Security Settings
  → Open: https://myaccount.google.com/security
  → Sign in if prompted
  
Step 2: Look for "2-Step Verification"
  → Scroll down on the Security page
  → You should see "How you sign in to Google"
  → Look for "2-Step Verification" (might also say "2-Factor Authentication")
  
Step 3: Click on "2-Step Verification"
  → It might say "OFF" or "Not set up"
  → Click it to start setup
  
Step 4: Add Your Phone Number
  → Google will ask for your phone number
  → Enter your phone number (make sure it's correct!)
  → Choose: Text message (SMS) or Phone call
  → Click "Send code"
  
Step 5: Enter the Verification Code
  → You'll receive a code on your phone
  → Enter it on the Google screen
  → Click "Turn On"
  
Step 6: Save Recovery Codes
  → Google will show backup recovery codes
  → SAVE THESE SAFELY (write them down!)
  → Click "Done"
  
✅ 2-Factor Authentication is now ENABLED

═════════════════════════════════════════════════════════════════════════

NOW: Generate App Password
═════════════════════════════════════════════════════════════════════════

Step 1: Go to App Passwords Page
  → Go to: https://myaccount.google.com/apppasswords
  → If you don't see this option, 2-FA might not be enabled yet
  → Wait a few minutes and refresh the page
  
Step 2: Select Device and App Type
  → Device dropdown: Select "Windows Computer" (or Mac/Linux)
  → App dropdown: Select "Mail"
  → DO NOT select "Google Drive" or other apps
  
Step 3: Generate the Password
  → Click the blue "Generate" button
  → Wait a moment...
  → A 16-character password will appear
  → Example: "abcd efgh ijkl mnop" (with spaces)
  
Step 4: Copy the Password
  → Highlight and copy the entire 16-character password
  → Remove any spaces when you copy it
  → Final format should be: abcdefghijklmnop (no spaces)
  
Step 5: The password is now ready to use
  → Google will remember it in the app passwords list
  → You can revoke it anytime from this page
  → You won't see it again after you leave the page

═════════════════════════════════════════════════════════════════════════

COMMON ISSUES AND FIXES:

ISSUE 1: "I don't see 2-Step Verification option"
  → Wait 5 minutes - sometimes Gmail is slow to update
  → Refresh the page (Ctrl+F5)
  → Try logging out and logging back in
  → Try in a different browser (Chrome, Firefox, Edge)

ISSUE 2: "2-Step Verification setup won't work"
  → Make sure your phone number is correct
  → Check if SMS/texts are enabled on your phone
  → Try choosing "Phone call" instead of text
  → Make sure you're not in airplane mode

ISSUE 3: "I don't see App Passwords option after enabling 2FA"
  → Wait 30 seconds after enabling 2-Step Verification
  → Refresh the security page
  → Logout and login again
  → Try in an incognito/private browser window

ISSUE 4: "The password doesn't work when testing"
  → Make sure you copied ALL 16 characters
  → Check that there are no extra spaces in .env file
  → Verify you pasted it without any line breaks
  → Verify you selected "Mail" (not Google Drive or others)

═════════════════════════════════════════════════════════════════════════

STEP-BY-STEP WITH WHAT YOU'LL SEE:

Screen 1 - Google Account Security
  URL: https://myaccount.google.com/security
  You'll see: "How you sign in to Google" section
  Look for: "2-Step Verification" button
  
Screen 2 - 2-Step Verification Setup
  Title: "Add a recovery phone for your Google Account"
  Enter: Your real phone number
  Choose: SMS (text) or Call
  
Screen 3 - Code Entry
  Message: "Enter the 6-digit code from your phone"
  Enter: The code Google texted/called you
  
Screen 4 - Success
  Message: "2-Step Verification is now on"
  Save: The recovery codes (screenshot them!)
  
Screen 5 - Back to Security Settings
  URL: https://myaccount.google.com/security
  Now you should see: "App passwords" option (below 2-Step Verification)
  
Screen 6 - App Passwords
  URL: https://myaccount.google.com/apppasswords
  Dropdown 1: Select "Windows Computer" (or your device)
  Dropdown 2: Select "Mail"
  Button: Click "Generate"
  
Screen 7 - App Password Generated
  Message: "Your app password for Windows Computer and Mail:"
  Shows: Something like "abcd efgh ijkl mnop"
  Action: Click to copy, or manually select and copy

═════════════════════════════════════════════════════════════════════════

WHAT YOU'LL DO WITH THE PASSWORD:

1. Copy the 16-character password (remove spaces)
2. Open: C:\\Users\\abc\\Desktop\\Rangard\\rangard\\.env
3. Find line: GMAIL_APP_PASSWORD=your_16_char_app_password_here
4. Replace with: GMAIL_APP_PASSWORD=abcdefghijklmnop (your actual password)
5. Save the file
6. Run: python rangard/test_gmail_smtp.py
7. Email should work!

═════════════════════════════════════════════════════════════════════════

NEED MORE HELP?

If 2-Factor Authentication won't work:
  → Try with a backup phone number
  → Use an authenticator app instead of SMS (Google Authenticator)
  → Contact Google Support
  
If App Passwords still don't work after all this:
  → Alternative: Use a Gmail "Less Secure" app setting
  → Or: Ask me to switch to a different email provider

═════════════════════════════════════════════════════════════════════════
"""

if __name__ == "__main__":
    print(__doc__)
