# 🚀 How to Deploy RANGARD to Render - Step by Step

> Render is a free hosting platform perfect for deploying both backend and frontend. This guide takes you through deployment in about 30 minutes.

---

## What You'll Deploy

- **Backend API** - FastAPI on Python (on Render)
- **Frontend** - React/Vite (on Render)
- **Database** - PostgreSQL (PostgreSQL on Render)
- **Custom Domain** - Optional (your own domain)

---

## Prerequisites

Before starting, you need:

```
✅ RANGARD project on GitHub (public repo)
✅ Render account (free signup at render.com)
✅ Gmail SMTP configured (already done - rangard.safe@gmail.com)
✅ App password for Gmail (already done - qdnojvfkraocmptr)
✅ 30 minutes of time
```

---

## Step 1: Prepare Your GitHub Repository

### 1.1 Create GitHub Repository

1. Go to https://github.com/new
2. Create public repository: `rangard` or `rangard-app`
3. Initialize with README
4. **Clone to your computer** (or push existing):
   ```bash
   git init
   git add .
   git commit -m "Initial commit - RANGARD application"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/rangard.git
   git push -u origin main
   ```

### 1.2 Create Required Files for Render

**File 1: `Procfile`** (tells Render how to start backend)
```
web: cd rangard && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```
Create at: `c:\Users\abc\Desktop\Rangard\Procfile`

**File 2: `requirements.txt`** - Already exists, ensure it has:
```
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
aiosqlite==0.19.0
asyncpg==0.29.0
pydantic-settings==2.1.0
python-multipart==0.0.6
pydantic==2.5.0
argon2-cffi==23.1.0
```

**File 3: `runtime.txt`** (specifies Python version)
```
python-3.11.7
```
Create at: `c:\Users\abc\Desktop\Rangard\runtime.txt`

**File 4: `build.sh`** (build script)
```bash
#!/bin/bash
set -o errexit

cd rangard
pip install -r requirements.txt

# Create tables if needed
python -c "
import asyncio
from app.core.database import create_tables
asyncio.run(create_tables())
"
```
Create at: `c:\Users\abc\Desktop\Rangard\build.sh`

Make it executable:
```bash
chmod +x build.sh
```

### 1.3 Update Frontend Build

**Ensure `.env` exists in frontend:** `frontend/.env`
```env
VITE_API_URL=https://your-backend-url.onrender.com
```

---

## Step 2: Deploy Backend API

### 2.1 Create Backend Service on Render

1. Go to https://dashboard.render.com
2. Click **+ New** → **Web Service**
3. Connect your GitHub repository
4. Fill in details:
   ```
   Name: rangard-api
   Environment: Python 3
   Region: Choose closest to you (e.g., Virginia)
   Branch: main
   Build Command: bash build.sh
   Start Command: cd rangard && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

### 2.2 Add Environment Variables

In Render dashboard, go to **Settings** → **Environment**

Add these variables:
```env
APP_NAME=RANGARD
APP_ENV=production
SECRET_KEY=rangard2024secretkeyforjwtauthentication123456789abc

# Database (will be created next)
DATABASE_URL=postgresql://user:password@host:5432/rangard
DATABASE_SYNC_URL=postgresql://user:password@host:5432/rangard

# Frontend & Backend URLs
FRONTEND_URL=https://rangard-frontend.onrender.com
BACKEND_URL=https://rangard-api.onrender.com

# Email (already configured)
EMAIL_FROM=rangard.safe@gmail.com
EMAIL_FROM_NAME=RANGARD Security
GMAIL_APP_PASSWORD=qdnojvfkraocmptr

# Blockchain (demo mode if no Infura key)
INFURA_PROJECT_ID=your_infura_key_here_optional
ETHEREUM_NETWORK=sepolia
CONTRACT_ADDRESS=0x0000000000000000000000000000000000000000
WALLET_PRIVATE_KEY=0x0000000000000000000000000000000000000000000000000000000000000000

# CORS
ALLOWED_ORIGINS=https://rangard-frontend.onrender.com,https://your-custom-domain.com

# File Storage (optional - use local disk)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
S3_BUCKET_NAME=

# Blockchain
INFURA_PROJECT_ID=
```

### 2.3 Create PostgreSQL Database

1. In Render dashboard, click **+ New** → **PostgreSQL**
2. Fill in:
   ```
   Name: rangard-db
   Database: rangard
   User: postgres
   Region: Same as API (Virginia)
   ```
3. Wait for creation (5 minutes)
4. Copy the **Internal Database URL** from dashboard
5. Paste into `DATABASE_URL` and `DATABASE_SYNC_URL` in your API environment

### 2.4 Wait for Backend Deploy

- Render will build and deploy automatically
- Check **Logs** tab for progress
- When done, you'll see a green checkmark
- Your backend URL: `https://rangard-api.onrender.com`
- Test it: https://rangard-api.onrender.com/docs

---

## Step 3: Build Frontend

### 3.1 Build React App Locally

In your local `rangard` folder:

```bash
cd frontend
npm install
npm run build
```

This creates `dist/` folder with production build.

### 3.2 Create `dist` and Push to GitHub

```bash
git add frontend/dist
git commit -m "Add frontend build"
git push
```

---

## Step 4: Deploy Frontend

### 4.1 Create Frontend Service on Render

1. Go to https://dashboard.render.com
2. Click **+ New** → **Static Site**
3. Connect GitHub repository
4. Fill in:
   ```
   Name: rangard-frontend
   Branch: main
   Build Command: cd frontend && npm install && npm run build
   Publish Directory: frontend/dist
   ```

### 4.2 Wait for Deploy

- Render will build and deploy
- When done: `https://rangard-frontend.onrender.com`

---

## Step 5: Configure Environment Variables

### Update Frontend Environment

After backend is deployed, update frontend `.env`:

```env
VITE_API_URL=https://rangard-api.onrender.com
```

Then rebuild:
```bash
cd frontend
npm run build
git add .
git push
```

### Update Backend URLs

In backend environment variables:
```env
FRONTEND_URL=https://rangard-frontend.onrender.com
BACKEND_URL=https://rangard-api.onrender.com
```

Render will auto-restart the service.

---

## Step 6: Test Everything

### 6.1 Test Backend API
```
Visit: https://rangard-api.onrender.com/docs
You should see Swagger UI with all endpoints
```

### 6.2 Test Frontend
```
Visit: https://rangard-frontend.onrender.com
Should load the React app
```

### 6.3 Test Registration Flow
```
1. Go to frontend → Click Register
2. Create account with real email
3. Check email for verification link
4. Click link - should verify
5. Login and upload file to test
```

### 6.4 Test Threat Alerts (Optional)
```
1. Verify your email
2. Upload a test malware file (simulated)
3. Check email for threat alert
```

---

## Step 7: Custom Domain (Optional)

### 7.1 Add Custom Domain to Backend

1. Render Dashboard → `rangard-api` service
2. Go to **Settings** → **Custom Domains**
3. Click **Add Custom Domain**
4. Enter: `api.yourdomain.com`
5. Follow DNS instructions (add CNAME record to your domain registrar)

### 7.2 Add Custom Domain to Frontend

1. Render Dashboard → `rangard-frontend` service
2. Go to **Settings** → **Custom Domains**
3. Click **Add Custom Domain**
4. Enter: `rangard.yourdomain.com` (or just `yourdomain.com`)
5. Follow DNS instructions

### 7.3 Update Environment Variables

Update backend environment:
```env
FRONTEND_URL=https://rangard.yourdomain.com
BACKEND_URL=https://api.yourdomain.com
```

---

## Complete Deployment Checklist

- [ ] GitHub repository created and pushed
- [ ] `Procfile`, `runtime.txt`, `build.sh` created
- [ ] Backend API deployed on Render
- [ ] PostgreSQL database created on Render
- [ ] Database URL added to backend environment
- [ ] Frontend built (`npm run build`)
- [ ] Frontend deployed on Render
- [ ] Frontend environment variables updated
- [ ] Backend environment variables updated
- [ ] Test registration flow works
- [ ] Test verification email arrives
- [ ] Test threat alerts work
- [ ] Custom domain configured (optional)
- [ ] SSL certificate auto-assigned by Render (automatic)

---

## Troubleshooting

### Backend Won't Start
1. Check **Logs** in Render dashboard
2. Common issue: Wrong DATABASE_URL
3. Solution: Copy exact PostgreSQL URL from database service
4. Wait for databases to be ready (can take 2-5 minutes)

### Verification Links Not Working
1. Check that `FRONTEND_URL` is correct in backend env
2. Frontend must be serving on the Render domain
3. Test with backend logs: `rangard-api` → **Logs**

### Emails Not Sending
1. Check Gmail SMTP password is correct
2. Verify `EMAIL_FROM=rangard.safe@gmail.com`
3. Check if Gmail account needs less secure apps enabled
4. View logs: `rangard-api` → **Logs** → search "Email"

### Frontend 404 Errors
1. Ensure `VITE_API_URL` points to correct backend
2. Frontend must be rebuilt after env changes
3. Clear browser cache and reload

### Database Connection Errors
1. Wait 5+ minutes after creating database
2. Verify `DATABASE_URL` format is correct
3. Test with simple query in Render console

---

## File Structure on GitHub

Your repo should look like:
```
rangard/
├── Procfile                    ← Added
├── runtime.txt                 ← Added
├── build.sh                    ← Added
├── requirements.txt            ← Updated
├── rangard/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── core/
│   │   └── ...
│   └── ...
├── frontend/
│   ├── dist/                   ← Will be created by build
│   ├── src/
│   ├── package.json
│   └── ...
└── README.md
```

---

## After Deployment

### Monitor Your Application
- Check **Logs** regularly for errors
- Monitor database performance
- Check email sending logs for bounces

### Keep Updated
- Set up auto-deploy on main branch push
- Test changes on staging before pushing to main
- Keep dependencies updated (run `npm audit` and `pip check`)

### Backup Database
- Use Render's automatic backups (included in paid plans)
- Or manually export data with PostgreSQL tools

### Scale Up If Needed
- If traffic increases, upgrade Render plan
- Add more replicas for backend
- Consider CDN for frontend static files

---

## Security Checklist

- [ ] `SECRET_KEY` is unique and strong (not the default)
- [ ] Gmail SMTP password is correct
- [ ] Database credentials are secure
- [ ] HTTPS is enabled (automatic on Render)
- [ ] ALLOWED_ORIGINS includes only your domains
- [ ] Environment variables are set (never commit .env to GitHub)
- [ ] No API keys in code or git history

---

## Cost

### Free Tier (Render)
- ✅ Backend API: Up to 750 hours/month free
- ✅ Frontend: Unlimited free static sites
- ✅ Database: 90 days free PostgreSQL instance

**Total: $0/month** (after free tier expires: ~$10-20/month)

---

## Support & Resources

- **Render Docs**: https://render.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React/Vite Docs**: https://vitejs.dev/

---

## Next Steps

After deployment:
1. ✅ Test all features (register, verify, scan, alerts)
2. ✅ Monitor logs for errors
3. ✅ Set up custom domain
4. ✅ Invite users to try the application
5. ✅ Collect feedback and iterate

---

## Summary

**You now have:**
- Production-ready API running 24/7
- Frontend accessible to anyone
- PostgreSQL database for persistence
- Email alerts working
- Automatic SSL certificates
- Free hosting tier

**Your RANGARD app is LIVE! 🚀**

---

**Questions?** Check the logs in Render dashboard or consult the troubleshooting section above.
