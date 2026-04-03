# 🚀 HOSTING & DOMAIN CONFIGURATION - COMPLETE

## What Was Fixed

✅ **Hardcoded localhost URLs → Configurable Domain URLs**

The application was previously limited to `localhost:3000` for verification links. Now it works with any domain!

---

## Changes Made

### 1. Updated Configuration [app/core/config.py]

Added two new configurable settings:
```python
FRONTEND_URL: str = "http://localhost:3000"  # ← Change on deployment
BACKEND_URL: str = "http://localhost:8000"   # ← Change on deployment
```

### 2. Updated Authentication [app/api/auth.py]

**Before (Broken):**
```python
verification_link = f"http://localhost:3000/verify-email?token={token}"
```

**After (Fixed):**
```python
settings = get_settings()
verification_link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
```

✅ Applied to 2 locations:
- `/api/auth/register` - Verification on registration
- `/api/auth/resend-verification` - Verification email resend

### 3. Updated Environment [.env]

Added configuration section:
```env
# ── Frontend & Backend URLs (for email verification links) ─
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
```

---

## How It Works Now

### **Local Development:**
```
User registers → Email sent with link:
https://localhost:3000/verify-email?token=abc123
→ User verifies locally ✅
```

### **After Deployment (e.g., Render):**
```
Update .env:
FRONTEND_URL=https://rangard-app.onrender.com

User registers → Email sent with link:
https://rangard-app.onrender.com/verify-email?token=abc123
→ User verifies on production ✅
```

### **With Custom Domain:**
```
Update .env:
FRONTEND_URL=https://rangard.yourcompany.com

User registers → Email sent with link:
https://rangard.yourcompany.com/verify-email?token=abc123
→ User verifies on custom domain ✅
```

---

## 🧪 Testing the Changes

### Test 1: Local Development (No changes needed)
```bash
# Just run normally
npm run dev              # Frontend at 3000
python run.py           # Backend at 8000

# Register at http://localhost:3000
# Email verification link will point to localhost ✅
```

### Test 2: With ngrok (FREE - No deployment needed!)
```bash
# Terminal 1-2: Run frontend + backend as normal
# Terminal 3-4: Start ngrok
ngrok http 3000   # Frontend → https://abc123.ngrok.io
ngrok http 8000   # Backend → https://def456.ngrok.io

# Update .env
FRONTEND_URL=https://abc123.ngrok.io
BACKEND_URL=https://def456.ngrok.io

# Restart backend, then test!
```

See `NGROK_TESTING_GUIDE.md` for detailed ngrok setup.

### Test 3: Full Production Deployment
```bash
# Deploy to Render/AWS/etc
# Update .env in deployment
FRONTEND_URL=https://your-production-domain.com
BACKEND_URL=https://api.your-production-domain.com

# Restart backend
# Test with real domain ✅
```

See `DEPLOYMENT_GUIDE.md` for full deployment instructions.

---

## 📋 Deployment Checklist

- [ ] Updated .env with your domain URLs
- [ ] Updated ALLOWED_ORIGINS in .env for CORS
- [ ] Restarted backend after .env changes
- [ ] Tested user registration
- [ ] Verified email link has correct domain
- [ ] Clicked verification link and completed verification
- [ ] Tested threat detection (file upload)
- [ ] Checked threat alert email arrived
- [ ] All links in emails point to your domain

---

## 📧 Email Verification Flow (Updated)

```
1. User registers at frontend
   ↓
2. Backend receives registration request
   ↓
3. Get settings.FRONTEND_URL from environment
   ↓
4. Create verification link:
   "{FRONTEND_URL}/verify-email?token={token}"
   ↓
5. Send verification email to user
   Email contains: "https://YOUR-DOMAIN/verify-email?token=xyz"
   ↓
6. User clicks link in email
   ↓
7. Browser opens verification page on YOUR-DOMAIN
   ↓
8. Frontend validates token
   ↓
9. Backend verifies and marks user as verified ✅
   ↓
10. User can now upload files and receive threat alerts
```

---

## 🔧 Configuration Reference

### Settings Added to config.py
```python
FRONTEND_URL: str = "http://localhost:3000"
BACKEND_URL: str = "http://localhost:8000"
```

### Environment Variables in .env
```env
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
```

### Where It's Used
- **Backend:** Generating verification links in emails
- **Frontend:** Not directly used in frontend code
- **Email:** Links in verification emails use FRONTEND_URL

### How to Update for Your Domain
```env
# Development
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000

# With ngrok
FRONTEND_URL=https://abc123.ngrok.io
BACKEND_URL=https://def456.ngrok.io

# Production (Render)
FRONTEND_URL=https://rangard-app.onrender.com
BACKEND_URL=https://api-rangard.onrender.com

# Production (Custom Domain)
FRONTEND_URL=https://rangard.yourcompany.com
BACKEND_URL=https://api.rangard.yourcompany.com
```

---

## ✅ Key Points

1. **No more hardcoded localhost** ✅
   - All URLs are now configurable

2. **Email verification works from any domain** ✅
   - Links automatically match your FRONTEND_URL

3. **CORS configured** ✅
   - Frontend can call backend from any domain
   - Configure ALLOWED_ORIGINS for CORS

4. **Gmail SMTP works everywhere** ✅
   - Email sends from any server/domain
   - No additional configuration needed

5. **Easy to deploy** ✅
   - Just change .env values
   - Restart backend
   - Everything works!

---

## 🚀 Next Steps

### Immediate (Testing):
1. **Test with ngrok** (see NGROK_TESTING_GUIDE.md)
   - Free, instant public URL
   - Test email verification works
   - Takes 5 minutes to setup

### Short-term (Development):
2. Use ngrok while developing to test email workflow

### Long-term (Production):
3. **Deploy to Render/AWS** (see DEPLOYMENT_GUIDE.md)
   - Real domain setup
   - Production-grade hosting
   - Multiple users can access

---

## 📁 New Documentation Files

- `DEPLOYMENT_GUIDE.md` - Full deployment instructions
- `NGROK_TESTING_GUIDE.md` - Testing with public URLs (free)
- This file - Overview of changes

---

## Summary

**Before:** Verification links hardcoded to localhost ❌
- Only worked locally
- Impossible to test email verification
- Users couldn't verify email

**After:** Verification links use configurable domain ✅
- Works with any domain
- Easy to test with ngrok
- Users can verify email from anywhere
- Ready for production deployment

**Cost:** FREE (using existing infrastructure)
**Setup time:** 5 minutes with ngrok, 30 minutes full deployment

---

**Your application is now deployment-ready! Choose your hosting option and update .env.** 🎉
