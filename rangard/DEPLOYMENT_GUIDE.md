# RANGARD - DEPLOYMENT & HOSTING GUIDE

## 🚀 Quick Overview

Your application is now configured to work with any domain! The verification links will automatically use your hosted domain once deployed.

---

## ⚙️ Configuration for Hosting

### Updated Files
✅ `app/core/config.py` - Added `FRONTEND_URL` and `BACKEND_URL` settings
✅ `app/api/auth.py` - Updated to use configurable URLs instead of hardcoded localhost
✅ `.env` - Added frontend and backend URL configuration

### How It Works

**Before (Broken):**
```python
verification_link = f"http://localhost:3000/verify-email?token={token}"
# Users could only verify on localhost!
```

**After (Fixed):**
```python
verification_link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
# Works with any domain!
```

---

## 📋 Deployment Checklist

Before deploying, you need:

### 1. Domain Name
- ✅ Purchase a domain (e.g., rangard.app, myrangard.io)
- ✅ Point DNS to your hosting provider

### 2. Hosting Provider
Choose one:
- **Render** (Recommended - free tier) - Railway, Vercel - Good for frontend
- **Heroku** (paid)
- **AWS** (complex)
- **DigitalOcean** (good for VPS)
- **Linode** (VPS option)

### 3. Email Configuration
- ✅ Gmail SMTP ready (rangard.safe@gmail.com)
- ✅ 16-char app password configured
- ✅ Will work from any domain

### 4. SSL Certificate
- ✅ Required for HTTPS (any hosting provider provides free)
- ✅ Automatic with Render, Vercel, Railway

---

## 🎯 Recommended: Deploy on Render (FREE)

### Step 1: Prepare Your Code

Update `.env` with your domain:
```env
# YOUR ACTUAL DOMAIN (replace with your domain)
FRONTEND_URL=https://rangard-frontend.onrender.com
BACKEND_URL=https://rangard-backend.onrender.com

# Or if using custom domain:
FRONTEND_URL=https://rangard.yourdomain.com
BACKEND_URL=https://api.yourdomain.com

ALLOWED_ORIGINS=https://rangard-frontend.onrender.com,https://rangard-backend.onrender.com

# Keep email config
EMAIL_FROM=rangard.safe@gmail.com
GMAIL_APP_PASSWORD=qdnojvfkraocmptr
```

### Step 2: Push to GitHub

```bash
git init
git add .
git commit -m "Ready for deployment"
git remote add origin https://github.com/yourusername/rangard.git
git branch -M main
git push -u origin main
```

### Step 3: Deploy Backend on Render

1. Go to **render.com**
2. Click **+ New**
3. Select **Web Service**
4. Choose your GitHub repository
5. Configure:
   - **Name:** rangard-backend
   - **Runtime:** Python 3.11
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `python rangard/run.py` or `cd rangard && python run.py`
   - **Plan:** Free (or paid)

6. **Environment Variables:**
   ```
   FRONTEND_URL=https://rangard-frontend.onrender.com
   BACKEND_URL=https://rangard-backend.onrender.com
   ALLOWED_ORIGINS=https://rangard-frontend.onrender.com
   GMAIL_APP_PASSWORD=qdnojvfkraocmptr
   EMAIL_FROM=rangard.safe@gmail.com
   APP_ENV=production
   ```

7. Click **Deploy**

### Step 4: Deploy Frontend on Render

1. Click **+ New**
2. Select **Static Site**
3. Choose your GitHub repository
4. Configure:
   - **Name:** rangard-frontend
   - **Build command:** `cd frontend && npm install && npm run build`
   - **Publish directory:** `frontend/dist`

5. Click **Deploy**

### Step 5: Update verification links

After deployment, your backend will automatically generate links like:
```
https://rangard-frontend.onrender.com/verify-email?token=abc123xyz...
```

---

## 🔄 Alternative: Docker + Hosting

### Create Docker files

**Dockerfile (Backend):**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "rangard/run.py"]
```

**Dockerfile.frontend:**
```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY frontend/ .
RUN npm install
RUN npm run build
RUN npm install -g serve
CMD ["serve", "-s", "dist", "-l", "3000"]
```

---

## 📬 Email Verification Flow (After Deployment)

### User Registration:
1. User registers at: `https://rangard-frontend.onrender.com/register`
2. System sends verification email with:
   ```
   https://rangard-frontend.onrender.com/verify-email?token=abc123...
   ```
3. User clicks link → Frontend validates token
4. Authorization header: `Authorization: Bearer <token>`
5. Frontend calls: `POST https://rangard-backend.onrender.com/api/auth/verify-email`
6. Backend verifies the token and marks user as verified
7. ✅ User can now use all features!

---

## 🔐 Before Going Live - Security Checklist

### Backend Security:
```env
# Change these for production!
SECRET_KEY=<generate-random-32-chars>
ALLOWED_ORIGINS=https://yourdomain.com
APP_ENV=production

# HTTPS Only
FRONTEND_URL=https://yourdomain.com
BACKEND_URL=https://api.yourdomain.com
```

### Generate Random Secret Key:
```python
import secrets
print(secrets.token_urlsafe(32))
```

### Database:
- ❌ Replace SQLite with PostgreSQL for production
- ✅ Use managed database from hosting provider

### Gmail:
- ✅ Already configured with app password
- ✅ Works from any domain automatically

---

## 🧪 Test After Deployment

1. **Register new user:**
   - Go to frontend URL
   - Register with: `rhythmbhatnagar.cse22@jimsgn.org`
   - Check email for verification link
   - **Verification link should have ACTUAL domain, not localhost!**

2. **Verify email:**
   - Click the link in the email
   - Frontend redirects to verification page
   - Backend processes and marks as verified
   - ✅ Should see "Email verified!" message

3. **Test threat alerts:**
   - Upload a suspicious file
   - Should receive email alert with proper domain links

---

## 📊 Current Configuration Status

| Component | Local Dev | After Deploy |
|-----------|-----------|--------------|
| Frontend | http://localhost:3000 | https://rangard-frontend.onrender.com |
| Backend | http://127.0.0.1:8000 | https://rangard-backend.onrender.com |
| Email From | rangard.safe@gmail.com | rangard.safe@gmail.com (same) |
| Verification Link | localhost link | Production domain link ✅ |
| CORS | localhost allowed | Your domain allowed ✅ |

---

## 💡 Key Points

✅ **No more hardcoded localhost** - Uses configurable URLs
✅ **Email links work everywhere** - Automatically use your domain
✅ **CORS configured** - Allows frontend to call backend
✅ **Email service ready** - Gmail SMTP works from any server
✅ **One .env file** - All configuration in one place

---

## 🚀 Next Steps

1. **Choose hosting provider** (Render recommended)
2. **Update .env with your domain**
3. **Push to GitHub**
4. **Deploy on Render**
5. **Test registration + verification**
6. **Send verification links to users!**

---

## 🆘 Troubleshooting

### Verification link returns 404
- Check `FRONTEND_URL` in `.env`
- Verify `/verify-email` route exists in frontend

### Email links point to localhost
- Update `FRONTEND_URL` in `.env`
- Restart backend service
- Re-register user

### CORS errors in browser console
- Update `ALLOWED_ORIGINS` in `.env`
- Format: `https://yourdomain.com,https://api.yourdomain.com`

### Email not sent
- Check `GMAIL_APP_PASSWORD` is correct
- Verify `EMAIL_FROM` matches Gmail account
- Check backend logs for SMTP errors

---

## 📞 Support

For issues:
1. Check backend logs
2. Verify all URL settings in `.env`
3. Test email sending with: `python test_master_email_system.py`
4. Ensure frontend and backend are on same origin or CORS configured

---

**Your application is now ready for production deployment! 🎉**
