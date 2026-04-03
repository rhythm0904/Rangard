# QUICK TEST WITH NGROK - Get Public URLs for Local App

If you want to test with real email verification links before full deployment, use **ngrok**!

## 📌 What is ngrok?

ngrok creates a **public URL** that points to your local application. Perfect for:
- Testing email verification links
- Sharing with friends
- Testing on mobile devices
- Before full deployment

---

## ⚡ Quick Setup (5 minutes)

### Step 1: Install ngrok

```bash
# Option A: Download from https://ngrok.com/download
# Option B: Using Chocolatey (Windows)
choco install ngrok

# Option C: Using npm
npm install -g ngrok
```

### Step 2: Create ngrok account (free)
1. Go to **https://ngrok.com**
2. Sign up (free)
3. Copy your **authtoken**

### Step 3: Connect ngrok
```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE
```

### Step 4: Get public URLs for both services

**Terminal 1 - Frontend:**
```bash
cd c:\Users\abc\Desktop\Rangard\rangard\frontend
ngrok http 3000
```

**Terminal 2 - Backend:**
```bash
ngrok http 8000
```

You'll see something like:
```
Frontend: https://abc123.ngrok.io
Backend:  https://def456.ngrok.io
```

### Step 5: Update .env

```env
FRONTEND_URL=https://abc123.ngrok.io
BACKEND_URL=https://def456.ngrok.io
ALLOWED_ORIGINS=https://abc123.ngrok.io,https://def456.ngrok.io
```

### Step 6: Restart backend

Kill and restart the backend server so it picks up the new URLs.

### Step 7: Test!

1. Go to: `https://abc123.ngrok.io`
2. Register with your email
3. **Check email for verification link**
4. Link should have your ngrok domain!
5. Click link → Should verify ✅

---

## 🔄 Important Notes

⚠️ **ngrok URLs change every time** you restart
- ✅ Restart with `--subdomain=myapp` for permanent URL (paid plan)
- Free plan: Update .env each time URLs change

⚠️ **ngrok requests take slightly longer** (usually fine for testing)

⚠️ **SSL/TLS automatically handled** by ngrok

---

## 📧 Email Testing with ngrok

When ngrok is running:

### User registers:
- Frontend: `https://abc123.ngrok.io/register`
- Enters email: `rhythmbhatnagar.cse22@jimsgn.org`

### Email received with link:
```
Click here to verify: https://abc123.ngrok.io/verify-email?token=xyz...
```

### User verifies:
- Clicks link → Opens in browser
- Frontend loads verification page
- Backend processes token
- ✅ Verified!

---

## 🎯 Full ngrok Testing Workflow

```bash
# Terminal 1: Frontend
cd c:\Users\abc\Desktop\Rangard\rangard\frontend
npm run dev
# (leaves running on http://localhost:3000)

# Terminal 2: Backend  
cd c:\Users\abc\Desktop\Rangard\rangard
python run.py
# (leaves running on http://127.0.0.1:8000)

# Terminal 3: ngrok Frontend
ngrok http 3000
# Copy: https://abc123.ngrok.io

# Terminal 4: ngrok Backend
ngrok http 8000
# Copy: https://def456.ngrok.io

# Terminal 5: Update .env
# Edit .env with ngrok URLs
FRONTEND_URL=https://abc123.ngrok.io
BACKEND_URL=https://def456.ngrok.io
ALLOWED_ORIGINS=https://abc123.ngrok.io,https://def456.ngrok.io

# Terminal 5 (continue): Restart backend
cd c:\Users\abc\Desktop\Rangard\rangard
python run.py
```

Now:
1. Open browser: `https://abc123.ngrok.io`
2. Register with real email
3. Verify with link from email
4. Test file upload and threat alerts
5. Check if threat email arrives ✅

---

## 🆚 ngrok vs Full Deployment

| Feature | ngrok | Render/AWS |
|---------|-------|------------|
| Setup time | 5 min | 30-60 min |
| Cost | Free | Free/Paid |
| URL stable | No (free) | Yes |
| For testing | ✅ Great | 🎯 Production |
| Verification links work | ✅ Yes | ✅ Yes |

---

## 💡 Pro Tips

1. **Test everything locally first**
   ```bash
   # Local test
   python test_master_email_system.py
   # Then use ngrok for email verification
   ```

2. **Screen capture the ngrok URLs**
   - They change each restart
   - Save them somewhere

3. **Use ngrok Web UI**
   - Inspector: `http://127.0.0.1:4040`
   - See all requests to your app

4. **Test on phone too**
   - Share ngrok URL with your phone
   - Test if responsive layout works
   - Test if email verification works on mobile

---

## 🆘 Troubleshooting ngrok

### "Invalid authtoken"
```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE
```

### Backend returns 500 error
- Check backend logs
- Verify `.env` settings are correct
- Restart backend after updating .env

### Email verification link doesn't open
- Check `FRONTEND_URL` in `.env`
- Make sure frontend is accessible via ngrok
- Check browser console for errors

### CORS error in browser
- Update `ALLOWED_ORIGINS` in `.env`
- Restart backend
- Hard refresh browser (Ctrl+Shift+R)

---

## ✅ After ngrok Testing

When you're ready for **real deployment**:

1. **Stop ngrok**
2. **Push code to GitHub**
3. **Deploy to Render** (or your choice)
4. **Update `.env` with production URLs**
5. **Test email verification works**
6. **Share with users!**

---

## Alternative: Use your own domain

If you already have a domain:

```env
FRONTEND_URL=https://your-domain.com
BACKEND_URL=https://api.your-domain.com
ALLOWED_ORIGINS=https://your-domain.com,https://api.your-domain.com
```

Then follow deployment guide in `DEPLOYMENT_GUIDE.md`

---

**ngrok is perfect for testing email verification before production deployment!**
