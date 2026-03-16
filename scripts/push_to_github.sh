#!/usr/bin/env bash
# RANGARD — Push to GitHub
# Run this once after downloading the zip

echo "Initialising RANGARD git repository..."

git init
git add .
git commit -m "feat: RANGARD v1.0 — AI ransomware detection platform

- FastAPI backend with async PostgreSQL
- RandomForest ML detector (14 behavioural features)  
- Blockchain file versioning via Ethereum/Infura
- Instant Quarantine with Fernet encryption
- ThreatPulse email alerts via SendGrid
- React frontend with animated RANGARD UI
- PDF report generation
- Docker + Nginx + CI/CD deployment ready"

git branch -M main
git remote add origin https://github.com/rhythm0904/rangard.git
git push -u origin main

echo ""
echo "✅ RANGARD is live at: https://github.com/rhythm0904/rangard"
echo ""
echo "Next steps:"
echo "  1. Go to github.com/rhythm0904/rangard/settings/secrets"
echo "     Add: EC2_HOST, EC2_USER, EC2_SSH_KEY, VERCEL_TOKEN"
echo "  2. bash scripts/setup.sh  (local dev)"
echo "  3. Follow docs/DEPLOYMENT.md for production"
