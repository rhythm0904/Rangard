# Deployment Guide

This guide covers deploying RANGARD to production on AWS EC2 (backend)
and Vercel (frontend). Total cost on free tiers: **$0/month** to start.

---

## Architecture overview

```
                    Internet
                       │
              ┌────────▼────────┐
              │   Vercel CDN    │  ← React frontend (free tier)
              │ (rangard.io)│
              └────────┬────────┘
                       │ HTTPS API calls
              ┌────────▼────────┐
              │  Nginx (EC2)    │  ← SSL termination + reverse proxy
              └────────┬────────┘
                       │
              ┌────────▼────────┐
              │  FastAPI (8000) │  ← Docker container
              ├─────────────────┤
              │  PostgreSQL     │  ← Docker container
              ├─────────────────┤
              │  Redis          │  ← Docker container
              └─────────────────┘
                       │
              ┌────────▼────────┐
              │  Infura / ETH   │  ← Blockchain (external)
              │  SendGrid       │  ← Email (external)
              │  AWS S3         │  ← File storage (optional)
              └─────────────────┘
```

---

## Step 1 — AWS EC2 instance

### Launch an instance
1. Go to AWS EC2 → Launch instance
2. Choose: **Ubuntu Server 22.04 LTS** (free tier eligible)
3. Instance type: **t2.micro** (free tier) or **t3.small** (recommended, ~$15/mo)
4. Storage: **20 GB** minimum
5. Security group — open these ports:
   - 22 (SSH — restrict to your IP)
   - 80 (HTTP — for Let's Encrypt verification)
   - 443 (HTTPS — public)
6. Create or select a key pair — download the `.pem` file

### Connect to your instance
```bash
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

### Install Docker
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker ubuntu
sudo apt install -y docker-compose-plugin nginx certbot python3-certbot-nginx
# Log out and back in for docker group to take effect
```

---

## Step 2 — Deploy the backend

### Clone and configure
```bash
sudo mkdir -p /opt/rangard
sudo chown ubuntu:ubuntu /opt/rangard
cd /opt/rangard

git clone https://github.com/rhythm0904/rangard.git .

cp .env.example .env
nano .env   # Fill in ALL required values
```

### Critical .env values for production
```env
APP_ENV=production
SECRET_KEY=$(openssl rand -hex 32)   # generate this, paste in

DATABASE_URL=postgresql+asyncpg://postgres:STRONG_PASSWORD@db:5432/rangard
DATABASE_SYNC_URL=postgresql+psycopg2://postgres:STRONG_PASSWORD@db:5432/rangard
POSTGRES_PASSWORD=STRONG_PASSWORD

ALLOWED_ORIGINS=https://your-frontend.vercel.app

SENDGRID_API_KEY=SG.your_real_key
EMAIL_FROM=alerts@rangard.app

INFURA_PROJECT_ID=your_infura_id
WALLET_PRIVATE_KEY=0xYOUR_PRIVATE_KEY
CONTRACT_ADDRESS=0xYOUR_DEPLOYED_CONTRACT
ETHEREUM_NETWORK=sepolia
```

### Train the ML model (run once)
```bash
cd /opt/rangard
docker-compose run --rm api python -c "
from app.ml.detector import train_demo_model
train_demo_model()
"
```

### Start all services
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
docker-compose logs -f api   # watch for errors
```

### Run database migrations
```bash
docker-compose exec api alembic upgrade head
# Or in development mode, tables are auto-created on startup
```

---

## Step 3 — SSL certificate + Nginx

### Point your domain to EC2
In your domain registrar's DNS, add an A record:
```
api.rangard.app  →  YOUR_EC2_PUBLIC_IP
```

Wait 5–10 minutes for DNS to propagate.

### Install the Nginx config
```bash
sudo cp /opt/rangard/nginx/rangard.conf /etc/nginx/sites-available/rangard
# Edit the domain name
sudo nano /etc/nginx/sites-available/rangard   # replace api.rangard.app
sudo ln -s /etc/nginx/sites-available/rangard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Get free SSL certificate
```bash
sudo certbot --nginx -d api.rangard.app
# Follow prompts — select option 2 (redirect HTTP to HTTPS)
```

Your API is now live at `https://api.rangard.app` 🎉

---

## Step 4 — Deploy the frontend to Vercel

### Method A: Vercel CLI (simplest)
```bash
cd frontend
npm install -g vercel
vercel login
vercel --prod
# Follow prompts
# Set environment variable: VITE_API_URL=https://api.rangard.app
```

### Method B: GitHub integration (recommended)
1. Push code to GitHub
2. Go to https://vercel.com → New Project → Import your repo
3. Set root directory to `frontend`
4. Add environment variable:
   - `VITE_API_URL` = `https://api.rangard.app`
5. Deploy — automatic deploys on every push to `main`

---

## Step 5 — Configure GitHub Actions secrets

In your GitHub repo → Settings → Secrets → Actions, add:

| Secret | Value |
|--------|-------|
| `EC2_HOST` | Your EC2 public IP or domain |
| `EC2_USER` | `ubuntu` |
| `EC2_SSH_KEY` | Contents of your `.pem` file |
| `VERCEL_TOKEN` | From vercel.com → Settings → Tokens |
| `VERCEL_ORG_ID` | From `vercel env ls` output |
| `VERCEL_PROJECT_ID` | From `vercel env ls` output |

Now every push to `main` automatically deploys both frontend and backend.

---

## Step 6 — Deploy the smart contract (optional)

Skip this if you're happy with demo mode (no real ETH needed for testing).

```bash
cd contracts
npm install

# Get free test ETH from: https://sepoliafaucet.com

npx hardhat run scripts/deploy.js --network sepolia
# Copy the printed contract address to your .env CONTRACT_ADDRESS
```

---

## Monitoring and maintenance

### Check service health
```bash
curl https://api.rangard.app/health
docker-compose ps
docker-compose logs --tail=50 api
```

### Update to latest version
```bash
cd /opt/rangard
git pull origin main
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build api
```

### Backup the database
```bash
docker-compose exec db pg_dump -U postgres rangard > backup-$(date +%Y%m%d).sql
```

### View quarantine directory
```bash
docker-compose exec api ls -la /var/rangard/quarantine/
```

---

## Estimated costs (AWS free tier)

| Service | Free tier | After free tier |
|---------|-----------|-----------------|
| EC2 t2.micro | 750 hrs/month (1 year) | ~$8/month |
| EBS storage 20GB | 30GB/month (1 year) | ~$2/month |
| Vercel frontend | 100GB bandwidth | Free (hobby plan) |
| Infura Ethereum | 100k req/day | Free |
| SendGrid email | 100 emails/day | Free |
| Sepolia test ETH | Free | Free (testnet) |

**Total first year: $0. After free tier: ~$10/month.**
