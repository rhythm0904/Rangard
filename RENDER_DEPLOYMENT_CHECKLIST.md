# ✅ RANGARD Render Deployment - Quick Checklist

## Pre-Deployment (Do This First)

### ✅ Step 1: Prepare GitHub Repository
- [ ] Create GitHub account (if needed): https://github.com/signup
- [ ] Create new public repository: https://github.com/new
  - Name it: `rangard` or `rangard-app`
- [ ] Clone locally or push existing code:
  ```bash
  git init
  git add .
  git commit -m "Initial RANGARD deployment"
  git branch -M main
  git remote add origin https://github.com/YOUR-USERNAME/rangard.git
  git push -u origin main
  ```

### ✅ Step 2: Verify Files Exist
Run this to check all required deployment files are in your repo:
```bash
# From c:\Users\abc\Desktop\Rangard\
ls -la Procfile runtime.txt build.sh .gitignore
```

**You should see:**
- ✅ `Procfile` - tells Render how to start backend
- ✅ `runtime.txt` - specifies Python version
- ✅ `build.sh` - build script for dependencies
- ✅ `.gitignore` - excludes sensitive files from git
- ✅ `requirem ents.txt` - backend dependencies (already exists)

---

## Render Deployment (30 minutes)

### ✅ Step 3: Create Render Account
1. Go to: https://render.com
2. Sign up (free) → Click "Sign Up"
3. Complete verification

### ✅ Step 4: Deploy Backend API

**4.1 Connect GitHub Repository**
1. In Render dashboard: Click **+ New** → **Web Service**
2. Click **Connect repository**
3. Authorize GitHub
4. Select your `rangard` repository

**4.2 Configure Backend Service**
- **Name:** `rangard-api`
- **Environment:** Python 3
- **Region:** Choose nearest to you (e.g., Oregon, Virginia)
- **Branch:** main
- **Runtime:** Python 3
- **Build Command:** `bash build.sh`
- **Start Command:**
  ```
  cd rangard && uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```
- Click **Create Web Service**

**4.3 Create PostgreSQL Database**
1. Click **+ New** → **PostgreSQL**
2. Configure:
   - **Name:** `rangard-db`
   - **Database:** rangard
   - **User:** postgres
   - **Region:** Same as API (e.g., Oregon)
   - **Plan:** Free
3. Click **Create Database**
4. Wait 5 minutes for creation
5. Copy **Internal Database URL** from details

**4.4 Add Environment Variables to Backend**
1. Go to `rangard-api` service
2. Click **Settings** → **Environment**
3. Add all these variables:

```
APP_NAME=RANGARD
APP_ENV=production
SECRET_KEY=rangard2024secretkeyforjwtauthentication123456789abc
FRONTEND_URL=https://rangard-frontend.onrender.com
BACKEND_URL=https://rangard-api.onrender.com
DATABASE_URL=[PASTE THE DATABASE_URL FROM STEP 4.3]
DATABASE_SYNC_URL=[PASTE THE SAME URL]
ALLOWED_ORIGINS=https://rangard-frontend.onrender.com,https://rangard-api.onrender.com
EMAIL_FROM=rangard.safe@gmail.com
EMAIL_FROM_NAME=RANGARD Security
GMAIL_APP_PASSWORD=qdnojvfkraocmptr
INFURA_PROJECT_ID=your_optional_key
ETHEREUM_NETWORK=sepolia
CONTRACT_ADDRESS=0x0000000000000000000000000000000000000000
WALLET_PRIVATE_KEY=0x0000000000000000000000000000000000000000000000000000000000000000
```

**Note:** Leave empty if you don't have values:
- INFURA_PROJECT_ID
- WALLET_PRIVATE_KEY
- CONTRACT_ADDRESS

**4.5 Wait for Backend Deploy**
- Check **Logs** tab
- Wait until you see: `Application startup complete`
- Visit: https://rangard-api.onrender.com/docs
- Should see Swagger UI ✅

---

### ✅ Step 5: Deploy Frontend

**5.1 Build Frontend Locally**
```bash
cd frontend
npm install
npm run build
```

**5.2 Update & Push to GitHub**
```bash
git add frontend/dist .env
git commit -m "Add frontend build for production"
git push
```

**5.3 Create Frontend Service**
1. In Render: Click **+ New** → **Static Site**
2. Connect your repository
3. Configure:
   - **Name:** `rangard-frontend`
   - **Branch:** main
   - **Build Command:** `cd frontend && npm install && npm run build`
   - **Publish Directory:** `frontend/dist`
4. Click **Create Static Site**

**5.4 Wait for Frontend Deploy**
- Check **Build & Deploys** tab
- Wait until you see green checkmark
- Visit: https://rangard-frontend.onrender.com
- Should see RANGARD homepage ✅

---

## ✅ Testing

### Test 1: Backend API
```
Visit: https://rangard-api.onrender.com/docs
Expected: Swagger UI shows all endpoints
Status: ✅ Working
```

### Test 2: Frontend Loads
```
Visit: https://rangard-frontend.onrender.com
Expected: RANGARD landing page with Sign Up button
Status: ✅ Working
```

### Test 3: Registration
```
1. Click "Sign Up"
2. Enter email (use REAL email like yourname@gmail.com)
3. Password: At least 8 characters
4. Full Name: Your Name
5. Click "Create Account"
```

### Test 4: Verify Email
```
1. Check your email inbox
2. Look for: "Verify Your Email - RANGARD"
3. From: rangard.safe@gmail.com
4. Click the verification link
5. You should see: "✅ Email verified!"
```

### Test 5: Upload File (Optional)
```
1. Go to dashboard
2. Upload a test file
3. Wait for AI analysis
4. Should see scan results
```

---

## URLs After Deployment

| Service | URL | Status |
|---------|-----|--------|
| **Backend API** | https://rangard-api.onrender.com | ✅ |
| **Frontend App** | https://rangard-frontend.onrender.com | ✅ |
| **API Docs** | https://rangard-api.onrender.com/docs | ✅ |
| **Database** | PostgreSQL on Render | ✅ |

---

## Optional: Custom Domain

### Add Your Own Domain (e.g., rangard.app)

**For Backend:**
1. Go to `rangard-api` → **Settings** → **Custom Domains**
2. Add: `api.yourdomain.com`
3. Follow DNS CNAME instructions

**For Frontend:**
1. Go to `rangard-frontend` → **Settings** → **Custom Domains**
2. Add: `rangard.yourdomain.com` or `yourdomain.com`
3. Follow DNS CNAME instructions

**Update Environment:**
1. Go to `rangard-api` → **Environment**
2. Update:
   ```
   FRONTEND_URL=https://rangard.yourdomain.com
   BACKEND_URL=https://api.yourdomain.com
   ```

---

## Troubleshooting

### ❌ Backend Won't Start
**Symptoms:** Red error in Logs

**Solution:**
1. Check Logs tab for error message
2. Most common: Wrong DATABASE_URL
3. Verify PostgreSQL is running (takes 2-5 minutes)
4. Restart Web Service manually

### ❌ Verification Emails Not Sending
**Symptoms:** Email doesn't arrive

**Solution:**
1. Check GMAIL_APP_PASSWORD is correct
2. Check email goes to spam folder
3. View backend logs for email errors
4. Verify FRONTEND_URL in environment

### ❌ Verification Link Shows 404
**Symptoms:** "Page not found" when clicking email link

**Solution:**
1. Ensure FRONTEND_URL ends without `/`
   - ✅ Correct: `https://rangard-frontend.onrender.com`
   - ❌ Wrong: `https://rangard-frontend.onrender.com/`
2. Frontend must be deployed
3. Browser cache - clear and retry

### ❌ Frontend Shows "Cannot Reach API"
**Symptoms:** Frontend loads but can't login/register

**Solution:**
1. Check VITE_API_URL in frontend .env
   - Should be: `https://rangard-api.onrender.com`
2. Rebuild frontend: `npm run build`
3. Push to GitHub
4. Render will auto-redeploy

---

## Cost

| Service | Price | Notes |
|---------|-------|-------|
| Backend (Web Service) | Free (750 hrs/mo) | After: $10/mo |
| Frontend (Static) | Free | Unlimited |
| Database (PostgreSQL) | Free (90 days) | After: $15/mo |
| **Total** | **$0** | ~$25/mo after trial |

---

## What to Share with Users

After deployment, share this link:
```
https://rangard-frontend.onrender.com
```

Users can:
- ✅ Create account
- ✅ Verify email
- ✅ Upload files to scan
- ✅ View threat analysis
- ✅ Receive email alerts

---

## Next Steps

1. ✅ Complete all steps above
2. ✅ Test registration & verification
3. ✅ (Optional) Add custom domain
4. ✅ Share with friends/beta users
5. ✅ Monitor logs for errors
6. ✅ Collect feedback

---

## Quick Links

- **Render Dashboard:** https://dashboard.render.com
- **Your Repository:** https://github.com/YOUR-USERNAME/rangard
- **GitHub Settings:** https://github.com/settings/tokens (if needed)

---

## Deployment Summary

**Before:** Application runs only on your computer at `localhost`

**After:** Application runs 24/7 on the internet at:
- `https://rangard-frontend.onrender.com` (anyone can access)
- `https://rangard-api.onrender.com` (API for app)

**Users worldwide can now:**
- Register accounts ✅
- Upload files to scan ✅
- Receive threat alerts ✅

---

## Questions?

If you get stuck:
1. Check **Logs** in Render dashboard
2. Read the full [RENDER_DEPLOYMENT_GUIDE.md](RENDER_DEPLOYMENT_GUIDE.md)
3. Check Render docs: https://render.com/docs

---

**Your RANGARD app is ready to be deployed! 🚀**

Follow the steps above and your app will be live in 30 minutes!
