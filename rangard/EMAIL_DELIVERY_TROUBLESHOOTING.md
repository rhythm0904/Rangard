# Email Delivery Troubleshooting Guide

## Problem
- ✅ Emails show as "sent" in the system
- ✅ Emails appear in Gmail "Sent" folder (rangard.safe@gmail.com)
- ❌ Users NOT receiving emails in their inbox

## Most Likely Cause: Gmail Spam Filters
Recent Gmail accounts or emails from new senders often go to **Spam/Promotions/Updates** folders.

---

## HOW TO TEST & FIX

### Step 1: Send Yourself a Test Email
```bash
cd c:\Users\abc\Desktop\Rangard\rangard
python test_email_delivery_diagnostic.py
```

When prompted, enter **YOUR PERSONAL GMAIL ADDRESS**.

### Step 2: Check All Gmail Folders
1. Go to https://mail.google.com
2. Check these folders **in order**:
   - ✅ **Inbox** (main messages)
   - ✅ **Promotions** (marketing emails)
   - ✅ **Updates** (account updates)
   - ✅ **Spam** (filtered messages)
   - ✅ **All Mail** (everything)

**Look for:** Email from "RANGARD Security <rangard.safe@gmail.com>"

### Step 3: Mark as NOT SPAM (if found in Spam)
If you find the email in Spam folder:
1. Click the email
2. Click the **⋮** (three dots) menu
3. Select **"Report not spam"**
4. This trains Gmail to trust RANGARD emails

### Step 4: Create a Filter (Optional but Recommended)
To ensure future RANGARD emails go to Inbox:
1. Click **⋮** (three dots) on the email
2. Select **"Filter messages like this"**
3. Check **"Never send to Spam"**
4. Click **"Create filter"**

---

## Email Content Details

### Verification Email
- **From:** RANGARD Security <rangard.safe@gmail.com>
- **Subject:** Verify Your Email - RANGARD
- **Content:** Professional HTML email with verification button
- **Should arrive in:** ~1-5 seconds

### Threat Alert Email
- **From:** RANGARD Security <rangard.safe@gmail.com>
- **Subject:** [RANGARD] THREAT_LEVEL Threat Detected — filename.txt
- **Content:** Detailed threat report with:
  - Filename
  - Threat level & confidence
  - Detected patterns
  - Dashboard link
  - Recommended actions

---

## Verify Email Headers (Advanced)

If you find an email from RANGARD, click it and select "Show original" to verify:

```
From: RANGARD Security <rangard.safe@gmail.com>
To: your.email@gmail.com
Date: [current date/time]
Message-ID: [unique ID]
Subject: Verify Your Email - RANGARD
MIME-Version: 1.0
Content-Type: multipart/alternative
```

✅ All headers should be present = emails are being sent correctly

---

## Current Email Configuration

**Sender:** rangard.safe@gmail.com
**SMTP Server:** smtp.gmail.com (port 587)
**Authentication:** App password (qdnojvfkraocmptr)
**Protocol:** TLS encrypted

**Email Headers Added:**
- ✅ From (with display name)
- ✅ To
- ✅ Reply-To
- ✅ Date
- ✅ Message-ID
- ✅ X-Mailer
- ✅ MIME-Version
- ✅ Priority headers

---

## Email Service Status

✅ **Emails ARE being sent successfully**
- Verified with test sending
- All SMTP connections working
- Gmail authentication successful
- Headers properly formatted

⚠️ **Delivery depends on:**
- Gmail spam filters
- Sender reputation
- Email content
- User email account settings

---

## What's Happening Behind the Scenes

When a user registers or uploads a suspicious file:

1. **Registration Email:**
   - User registers with email address
   - Verification email automatically sent
   - User should check inbox/spam folders
   - User clicks link to verify

2. **Threat Alert Email:**
   - File uploaded to system
   - ML detector identifies threat
   - System checks if user is verified
   - If verified: Threat alert email sent
   - If not verified: Alert not sent (user not verified)

---

## Action Items

### For Users:
1. Run the test: `python test_email_delivery_diagnostic.py`
2. Enter your Gmail address
3. Check ALL Gmail folders
4. Mark RANGARD as "Not Spam"
5. Create a filter for future emails

### For Admin:
1. Monitor email sending logs
2. Track which emails go to spam
3. Improve sender reputation over time

---

## Why Emails Go to Spam

New senders often get filtered because:
- **SPF/DKIM/DMARC:** Gmail checks email authentication
- **Sender Reputation:** New accounts have low trust score
- **Email Content:** HTML emails from unknown senders
- **User Behavior:** First email from new sender

**Solution:** Users need to mark emails as "Not Spam" to train Gmail.

---

## Expected Delivery Time

- **Verification email:** 1-5 seconds
- **Threat alert email:** 1-5 seconds
- **Gmail filtering:** 30 seconds to 2 minutes

If not received within 2 minutes, check spam folder.

---

## Support

If emails still don't arrive:
1. Check spam/promotions folders
2. Verify email address is correct during registration
3. Mark RANGARD as trusted sender
4. Contact support with email details

**System Status:** ✅ All emails are being sent successfully
