#!/usr/bin/env bash
# RANGARD — Developer Setup Script
# github.com/rhythm0904/rangard
set -e
GREEN='\033[0;32m'; BLUE='\033[0;34m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
info()    { echo -e "${BLUE}[rangard]${NC} $1"; }
success() { echo -e "${GREEN}[✓]${NC} $1"; }
warn()    { echo -e "${YELLOW}[!]${NC} $1"; }
error()   { echo -e "${RED}[✗]${NC} $1"; exit 1; }

echo ""
echo -e "${BLUE}╔══════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   RANGARD — Developer Setup          ║${NC}"
echo -e "${BLUE}║   github.com/rhythm0904/rangard      ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════╝${NC}"
echo ""

command -v python3 >/dev/null 2>&1 || error "Python 3 required. Install from python.org"
command -v docker  >/dev/null 2>&1 || error "Docker required. Install from docker.com"

info "Setting up Python virtual environment..."
[ ! -d "venv" ] && python3 -m venv venv && success "Created ./venv"
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
success "Python dependencies installed"

if command -v node >/dev/null 2>&1; then
  info "Installing frontend dependencies..."
  cd frontend && npm install --silent && cd ..
  success "Frontend dependencies installed"
fi

if [ ! -f ".env" ]; then
  cp .env.example .env
  SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
  if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s/CHANGE_ME_use_openssl_rand_hex_32/$SECRET/" .env
  else
    sed -i "s/CHANGE_ME_use_openssl_rand_hex_32/$SECRET/" .env
  fi
  success ".env created with random SECRET_KEY"
  warn "Add your SendGrid and Infura keys to .env when ready"
fi

info "Starting PostgreSQL and Redis..."
docker-compose up db redis -d --quiet-pull 2>/dev/null || docker compose up db redis -d
for i in {1..20}; do
  docker-compose exec -T db pg_isready -U postgres -q 2>/dev/null && break
  sleep 1
done
success "Database ready"

if [ ! -f "app/ml/model/rangard_rf.joblib" ]; then
  info "Training demo ML model (~10 seconds)..."
  python3 -c "from app.ml.detector import train_demo_model; train_demo_model()"
  success "Demo model trained"
fi

echo ""
echo -e "${GREEN}╔══════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Setup complete! 🛡️                 ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${BLUE}Start the API:${NC}"
echo -e "    ${YELLOW}source venv/bin/activate${NC}"
echo -e "    ${YELLOW}uvicorn app.main:app --reload --port 8000${NC}"
echo ""
echo -e "  ${BLUE}Start the frontend:${NC}"
echo -e "    ${YELLOW}cd frontend && npm run dev${NC}"
echo ""
echo -e "  ${BLUE}API docs:${NC}  ${YELLOW}http://localhost:8000/docs${NC}"
echo -e "  ${BLUE}Frontend:${NC}  ${YELLOW}http://localhost:3000${NC}"
echo ""
echo -e "  ${BLUE}Train on real data:${NC}"
echo -e "    ${YELLOW}python scripts/train_model.py --mode real \\${NC}"
echo -e "    ${YELLOW}  --clean-dir data/clean --ransom-dir data/ransomware${NC}"
echo ""
