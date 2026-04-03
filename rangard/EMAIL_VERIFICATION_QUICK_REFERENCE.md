# Email Verification - Quick Reference Guide

## TL;DR - How It Works

1. **User Registers** → Gets JWT token immediately
2. **Verification Email Sent** → With clickable link containing secure token
3. **User Clicks Link** → Frontend automatically verifies with backend
4. **Backend Validates Token** → Marks user as `is_verified = TRUE`
5. **Alert Emails Now Enabled** → User can receive threat notifications

---

## The 5-Step Process

### Step 1: Register
```
Frontend → POST /api/auth/register
Body: { email: "user@test.com", password: "Abc123456", full_name: "John" }
Response: JWT Token
```

### Step 2: Email Arrives
```
Subject: "Verify Your Email - RANGARD"
From: rangard.safe@gmail.com

Content:
  Thank you for registering!
  
  [Verify Your Email] ← This is a clickable link
  
  Link format:
  http://localhost:3000/verify-email?token=eyJhbGc...
```

### Step 3: User Clicks Link
```
Browser → Opens verification page
URL: http://localhost:3000/verify-email?token=eyJhbGc...

Frontend code extracts token from URL
Automatically calls: POST /api/auth/verify-email
```

### Step 4: Backend Verifies
```
Backend receives: { token: "eyJhbGc..." }

Process:
  1. Decode JWT token
  2. Extract email from token
  3. Check token expiration (must be < 24h old)
  4. Find user in database
  5. Set user.is_verified = TRUE ✓
  6. Save to database
  7. Return success
```

### Step 5: Success!
```
Frontend shows:
  ✅ Email verified!
  Your email user@test.com has been verified.
  🎉 You can now receive threat alert emails!
  
  Auto-redirects to /dashboard after 3 seconds
```

---

## After Verification: Alert Emails

### Unverified User Uploads Threat File
```
❌ NO EMAIL SENT
Message: "Email alerts disabled — verify your email"
But file IS scanned and quarantined
```

### Verified User Uploads Threat File
```
✅ EMAIL SENT!
Recipient: user@test.com

Subject: "🛡️ RANGARD Security Alert"
Content: 
  - Filename detected
  - Threat level (CRITICAL/HIGH/MEDIUM/LOW)
  - Confidence score
  - Detected patterns/signatures
  - Quarantine status
  - Link to dashboard
```

---

## Token Details

**What's in the Token:**
```python
{
  "email": "user@test.com",
  "exp": 1712332800,  # Expires 24 hours from now
  "iat": 1712246400   # Issued at
}
```

**How It's Created:**
```python
from app.core.security import create_email_verification_token

token = create_email_verification_token("user@test.com")
# Returns: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**How It's Verified:**
```python
from app.core.security import verify_email_token

payload = verify_email_token(token)
# Returns: { "email": "user@test.com", "exp": ..., "iat": ... }
# Throws: HTTPException if invalid/expired
```

---

## Database Impact

### Before Verification
```
User Table:
┌─────────────┬───────────────────┬───────────┐
│ email       │ is_verified       │ created   │
├─────────────┼───────────────────┼───────────┤
│ user@t.com  │ FALSE ❌          │ 2026-04-04│
└─────────────┴───────────────────┴───────────┘

↳ Can login: YES (has JWT token)
↳ Can upload files: YES
↳ Receive alerts: NO
```

### After Verification
```
User Table:
┌─────────────┬───────────────────┬───────────┐
│ email       │ is_verified       │ created   │
├─────────────┼───────────────────┼───────────┤
│ user@t.com  │ TRUE ✓            │ 2026-04-04│
└─────────────┴───────────────────┴───────────┘

↳ Can login: YES
↳ Can upload files: YES
↳ Receive alerts: YES ✓
```

---

## File References

| Component | File | Function |
|-----------|------|----------|
| **Register** | `app/api/auth.py` | `register()` |
| **Verify** | `app/api/auth.py` | `verify_email()` |
| **Resend** | `app/api/auth.py` | `resend_verification()` |
| **Token Creator** | `app/core/security.py` | `create_email_verification_token()` |
| **Token Validator** | `app/core/security.py` | `verify_email_token()` |
| **Email Template** | `app/services/email.py` | `EMAIL_VERIFICATION_HTML` |
| **Frontend UI** | `frontend/src/pages/VerifyEmailPage.jsx` | Component |
| **API Service** | `frontend/src/services/api.js` | `authApi.verifyEmail()` |

---

## Common Scenarios

### ✅ Happy Path
```
1. User registers with real email: john@gmail.com
2. Verification email arrives in inbox
3. User clicks verification link
4. Success! User is verified
5. User uploads file with malware
6. User receives threat alert email
```

### ⚠️ Email Doesn't Arrive
```
1. Check spam/promotions folder
2. Wait a few minutes (sometimes slow)
3. If still missing: User clicks "Resend verification email"
4. New email sent with fresh token
5. Try clicking link again
```

### ⏲️ Token Expires
```
1. User gets verification email
2. Waits more than 24 hours to click link
3. Clicks link
4. Error: "Token has expired"
5. User clicks "Resend verification email"
6. New token generated, fresh email sent
7. User verifies with new token
```

### 🔄 Already Verified
```
1. User's email is already verified
2. User refreshes page multiple times
3. Clicking verify link shows: "Email already verified"
4. No error, just informational
5. Frontend redirects to dashboard
```

---

## Settings & Configuration

### Environment Variables (`.env`)
```env
# Email verification
EMAIL_VERIFICATION_EXPIRE_HOURS=24

# Email service
EMAIL_FROM=rangard.safe@gmail.com
EMAIL_FROM_NAME=RANGARD Security
GMAIL_APP_PASSWORD=qdnojvfkraocmptr

# Frontend URLs (used in verification links)
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
```

### Verification Link Format
```
{FRONTEND_URL}/verify-email?token={TOKEN}

Example (Development):
http://localhost:3000/verify-email?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Example (Production):
https://rangard.example.com/verify-email?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Summary

✅ **Verification System is FULLY IMPLEMENTED**

- Tokens created with 24-hour expiration
- Emails sent via Gmail SMTP
- Verification page auto-validates tokens
- Threat alerts only sent to verified users
- Users can resend verification emails
- All API endpoints working correctly

**Your users will:**
1. Receive verification email after registration
2. Click link to verify (automatic process)
3. Receive threat alerts when malware detected
4. See verification status in their profile

Everything is ready! 🚀
