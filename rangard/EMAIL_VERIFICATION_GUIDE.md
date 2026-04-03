# Email Verification Flow - Complete Guide

## Overview

The email verification system ensures users verify their email address before receiving threat alerts. Here's how it works step by step:

## Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER REGISTRATION                              │
│  User fills form: email, password, full_name                     │
│  Frontend: POST /api/auth/register                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                 BACKEND PROCESSES                                 │
│                                                                   │
│  1. Create User in Database                                      │
│     - is_verified = FALSE (✗)                                    │
│     - Password hashed with Argon2                                │
│     - User ID generated                                          │
│                                                                   │
│  2. Generate Verification Token                                  │
│     - Token contains: email, expiration (24h)                    │
│     - Token signed with SECRET_KEY                               │
│     - Token format encoded in JWT                                │
│                                                                   │
│  3. Create Verification Link                                     │
│     - Format: {FRONTEND_URL}/verify-email?token={TOKEN}          │
│     - Example: http://localhost:3000/verify-email?token=abc...   │
│                                                                   │
│  4. Send Email via Gmail SMTP                                    │
│     - From: rangard.safe@gmail.com                               │
│     - Subject: "Verify Your Email - RANGARD"                     │
│     - Body: HTML + Plain Text with verification link             │
│     - Link is clickable: Opens browser to verification page      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              EMAIL RECEIVED BY USER                               │
│                                                                   │
│  "Verify Your Email - RANGARD"                                   │
│  ────────────────────────────                                    │
│                                                                   │
│  Hello,                                                           │
│                                                                   │
│  Thank you for registering with RANGARD!                         │
│                                                                   │
│  VERIFY YOUR EMAIL                                               │
│  ──────────────────                                              │
│  [Click to verify your email]  ← CLICKABLE BUTTON/LINK           │
│                                                                   │
│  This link is valid for 24 hours.                                │
│                                                                   │
│  ---                                                             │
│  © 2026 RANGARD Security                                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼ (User clicks link in email)
┌─────────────────────────────────────────────────────────────────┐
│          FRONTEND VERIFICATION PAGE LOADS                         │
│                                                                   │
│  Browser opens: {FRONTEND_URL}/verify-email?token={TOKEN}        │
│                                                                   │
│  VerifyEmailPage.jsx runs:                                       │
│  1. Extracts token from URL query parameter                      │
│  2. Automatically calls: POST /api/auth/verify-email             │
│  3. Shows "Verifying your email..." spinner                      │
│                                                                   │
│  User sees: Loading spinner                                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│             BACKEND VERIFIES TOKEN                                │
│                                                                   │
│  POST /api/auth/verify-email receives { token: "..." }           │
│                                                                   │
│  Backend:                                                         │
│  1. Decodes JWT token using SECRET_KEY                           │
│  2. Extracts email from token payload                            │
│  3. Checks token hasn't expired (24h limit)                      │
│  4. Finds user in database by email                              │
│  5. Updates: user.is_verified = TRUE (✓)                         │
│  6. Commits to database                                          │
│  7. Returns success response                                     │
│                                                                   │
│  If fails: Returns error (expired, invalid, etc)                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│          USER SEES SUCCESS MESSAGE                                │
│                                                                   │
│  ✅ Email verified!                                              │
│                                                                   │
│  Your email user@example.com has been verified.                  │
│                                                                   │
│  🎉 You can now receive threat alert emails!                     │
│                                                                   │
│  [Go to Dashboard]                                               │
│                                                                   │
│  Auto-redirects after 3 seconds to dashboard                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│           NOW USER CAN USE ALL FEATURES ✓                        │
│                                                                   │
│  ✓ Upload and scan files                                         │
│  ✓ Receive threat alert emails when malware detected             │
│  ✓ View scan history                                             │
│  ✓ Download PDF reports                                          │
│  ✓ Use all dashboard features                                    │
│                                                                   │
│  Key point: is_verified = TRUE in database                       │
│  So when threats are detected:                                   │
│  - Email alerts ARE sent                                         │
│  - User receives notifications                                   │
└─────────────────────────────────────────────────────────────────┘
```

## What Happens at Each Stage

### 1. Registration Endpoint
**Code:** `app/api/auth.py` line 126

```python
# User registers with email, password, full_name
verification_token = create_email_verification_token(user.email)

# Token is JWT containing: { email: "user@test.com", exp: 24h }
verification_link = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"

# Send email with the link
email_svc.send_email_verification(user.email, verification_link)
```

**What gets stored in database:**
- User record with `is_verified=False`
- User can login immediately (has JWT token)
- But threat alerts won't send yet

### 2. Email Sent to User
**Template:** `app/services/email.py` line 200+

The email contains:
- HTML formatted with nice design
- Plain text version for email clients
- One verification link in the format:
  ```
  http://localhost:3000/verify-email?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  ```

### 3. User Clicks Link
**Frontend:** `frontend/src/pages/VerifyEmailPage.jsx`

When user clicks the link:
1. Browser navigates to `/verify-email?token=...`
2. React component extracts `token` from URL
3. Automatically POSTs to `/api/auth/verify-email`
4. User sees loading spinner

### 4. Backend Verifies
**Code:** `app/api/auth.py` line 248

```python
@router.post("/verify-email")
async def verify_email(request, db):
    # Decode and verify the JWT token
    payload = verify_email_token(request.token)
    email = payload.get("email")
    
    # Find user by email
    user = db.query(User).filter(User.email == email).first()
    
    # Mark as verified!
    user.is_verified = True
    db.commit()
    
    return { "verified": true, "email": email }
```

### 5. User Sees Success
**Frontend shows:**
```
✅ Email verified!

Your email user@example.com has been verified.

🎉 You can now receive threat alert emails!

→ Redirects to /dashboard
```
```

### 2. **Email Verification Templates**
**File**: `app/services/email.py`
- HTML email template with verification link
- Plain text fallback email
- Professional design with security warnings

### 3. **New Endpoints**

#### Register User (Updated)
```
POST /api/auth/register
Body: { email, password, full_name }
Response: LoginResponse (with access_token)

Side Effect:
  - User is created with is_verified=False
  - Verification email sent to their address
  - They receive link to click for verification
```

#### Verify Email
```
POST /api/auth/verify-email
Body: { token }
Response: { message, email, verified }

Action:
  - Decodes verification token
  - Marks user email as verified
  - User can now receive threat alerts
```

#### Resend Verification Email
```
POST /api/auth/resend-verification
Headers: Authorization: Bearer {token}
Response: { message, verified }

Action:
  - Generates new verification token
  - Sends fresh verification email
  - Valid for authenticated users only
```

#### Get User Profile (Updated)
```
GET /api/auth/me
Response includes: is_verified (boolean)

Shows:
  - Current verification status
  - Whether user can receive alerts
```

### 4. **File Scanning Updates**
**File**: `app/api/scans.py`

When a file is detected as threatening:
```
✅ If email VERIFIED:
   → Threat alert email is sent immediately
   → Full notification to user

❌ If email NOT verified:
   → Alert email is SUPPRESSED
   → User sees message: "Email alerts disabled — verify your email"
   → No alerts sent to invalid/unverified addresses
```

### 5. **Database Changes**
**File**: `app/core/models.py`

User model updated with:
```python
is_verified: Column(Boolean, default=False, nullable=False)
```

Configuration added:
```python
EMAIL_VERIFICATION_EXPIRE_HOURS: int = 24
```

## How It Works (User Journey)

### Step 1: Registration
```
User enters: email@example.com + password
↓
RANGARD creates account with is_verified=False
↓
Sends verification email to email@example.com
↓
Email contains clickable link with secure token
↓
Frontend redirects user to: /verify-email?token={token}
```

### Step 2: Email Verification
```
User clicks link in email
↓
Frontend calls: POST /api/auth/verify-email with token
↓
Backend validates token (must be <24 hours old)
↓
Marks user as is_verified=True
↓
User can now receive threat alerts
```

### Step 3: File Upload & Threat Detection
```
User uploads file → AI analysis runs
↓
Threat detected (medium/high/critical)
↓
Check: Is user's email verified?
  ├─ YES → Send threat alert email immediately ✅
  └─ NO  → Suppress alert, show message in UI ❌
↓
File is quarantined regardless of email status
↓
User can see results in dashboard/scans
```

### Step 4: Resend Verification (if needed)
```
User hasn't received verification email
↓
Clicks "Resend verification email" in dashboard
↓
Backend generates new token
↓
Sends fresh verification email
↓
User can verify again
→ Link valid for another 24 hours
```

## Configuration

### Settings (in `.env`)
```env
# Email verification link duration
EMAIL_VERIFICATION_EXPIRE_HOURS=24

# Email service configuration
SENDGRID_API_KEY=SG.xxxxx
EMAIL_FROM=alerts@yourdomain.com
EMAIL_FROM_NAME=RANGARD Security
```

## Security Features

### 1. **Token Security**
- Tokens are JWTs signed with your SECRET_KEY
- Include expiration time (default: 24 hours)
- Type-checked to prevent misuse
- Can't verify registration JWTs as email tokens

### 2. **Email Validation**
- Only verified emails receive critical alerts
- Invalid/fake emails never receive notifications
- Reduces email bounces and spam complaints

### 3. **Resend Capability**
- Users can request fresh verification emails
- Prevents lockout if original email is lost
- Generates new secure token each time
- Old tokens automatically expire

### 4. **Threat Alert Control**
- Alerts only sent to verified addresses
- Unverified users still see results in dashboard
- Clear messaging about verification requirement
- No security gaps - files still quarantined

## API Response Examples

### Register (Success)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com"
}
```
User receives email with: "Click here to verify: https://yourapp.com/verify-email?token=..."

### Verify Email (Success)
```json
{
  "message": "Email verified successfully! You can now receive threat alerts.",
  "email": "user@example.com",
  "verified": true
}
```

### Verify Email (Error - Invalid Token)
```json
{
  "detail": "Invalid or expired verification token"
}
```

### Resend Verification (Success)
```json
{
  "message": "Verification email sent. Check your inbox!",
  "verified": false
}
```

### File Scan with Unverified Email
```json
{
  "scan_id": "550e8400-e29b-41d4-a716-446655440001",
  "status": "complete",
  "threat_level": "high",
  "confidence": 0.85,
  "quarantined": true,
  "message": "🚨 High threat detected — file quarantined immediately (Email alerts disabled — verify your email to receive notifications)"
}
```

## Frontend Integration Points

### 1. **Registration Form**
- Same as before - user enters email, password
- Backend automatically sends verification email
- No additional frontend changes needed

### 2. **Verification Page**
- URL: `/verify-email?token={verification_token}`
- Extracts token from URL parameter
- Calls: `POST /api/auth/verify-email` with token
- Shows confirmation message

### 3. **Dashboard/Settings**
- Show verification status
- Link to "Resend verification email"
- Clear messaging about alert requirements

### 4. **Upload Results**
- Message updates based on email verification status
- Warns unverified users to verify for alerts
- Link to resend verification

## Testing

### Test Files Provided
```
test_email_verification.py  # Complete flow test
test_register_http.py       # Registration test
test_file_scan.py           # File scan with alerts
```

### Manual Testing

1. **Register without verification**
   ```bash
   curl -X POST http://localhost:8000/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"Pass123456","full_name":"Test User"}'
   ```
   → User created with `is_verified=false`
   → Verification email logged in dev mode

2. **Verify email**
   ```bash
   # Generate token using: from app.core.security import create_email_verification_token
   # token = create_email_verification_token("test@example.com")
   
   curl -X POST http://localhost:8000/api/auth/verify-email \
     -H "Content-Type: application/json" \
     -d '{"token":"..."}'
   ```
   → User marked as verified

3. **Check profile**
   ```bash
   curl -H "Authorization: Bearer {token}" \
     http://localhost:8000/api/auth/me
   ```
   → Will show `"is_verified": true`

## Email Template

When user gets verification email, they see:

```
🛡️ Verify Your Email - RANGARD
────────────────────────────────

Hello,

Thanks for signing up for RANGARD! We need to verify your email address 
so we can send you threat alerts directly to this inbox.

[Verify Email Address →]

Or copy and paste this link in your browser:
https://localhost:3000/verify-email?token=eyJ...

⚠️ Security Note: This link will expire in 24 hours. 
   If you did not sign up for RANGARD, you can safely ignore this email.

Without email verification, you won't receive threat alerts when suspicious 
files are detected. We take your security seriously and only send emails 
when threats are detected in your scans.
```

## Production Recommendations

### 1. **Email Service Setup**
- SignGrid (recommended): Fast, reliable, webhooks
- AWS SES: Cost-effective, high volume
- Custom SMTP: Full control

### 2. **Verification Timeout**
- 24 hours is good default
- Adjust in `.env`: `EMAIL_VERIFICATION_EXPIRE_HOURS=48`
- Consider: 12 hours for high-security, 7 days for casual

### 3. **Rate Limiting**
- Limit resend requests: 1 per minute / 5 per hour
- Prevent email list farms
- Track failed verification attempts

### 4. **Migration**
If upgrading from older RANGARD:
```bash
# Reset is_verified for existing users (they'll need to re-verify)
UPDATE users SET is_verified=False;

# Or mark them verified automatically (less secure)
UPDATE users SET is_verified=True;
```

## Files Modified

1. ✅ `app/core/security.py` - Added token functions
2. ✅ `app/core/config.py` - Added verification timeout setting  
3. ✅ `app/services/email.py` - Added verification email template and send method
4. ✅ `app/api/auth.py` - Updated registration, added verify/resend endpoints
5. ✅ `app/api/scans.py` - Added verification check before sending alerts

## Summary

Your RANGARD application now:
- ✅ Ensures only real emails register
- ✅ Verifies email addresses before sending alerts
- ✅ Provides secure 24-hour verification tokens
- ✅ Allows alert resending if user loses initial email
- ✅ Prevents spam to invalid/unverified addresses
- ✅ Maintains threat detection for all users (verified or not)
- ✅ Quarantines dangerous files regardless of email status

**All users registering now MUST verify their email to receive threat alerts.**
Unverified users can still access the dashboard and see scan results, but won't get email notifications.

This significantly improves security by ensuring alerts only go to real, verified email addresses! 🛡️
