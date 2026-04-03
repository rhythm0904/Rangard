# Contributing to RANGARD

Thank you for your interest in contributing! This document explains how to get started.

---

## Getting started

### 1. Fork and clone

```bash
git clone https://github.com/YOUR_USERNAME/rangard.git
cd rangard
```

### 2. Set up the backend

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit with your values
docker-compose up db redis -d
uvicorn app.main:app --reload
```

### 3. Set up the frontend

```bash
cd frontend
npm install
npm run dev
```

API runs on http://localhost:8000, frontend on http://localhost:3000.

---

## Project structure

```
app/core/       ← Settings, DB, models, JWT
app/api/        ← FastAPI route handlers
app/ml/         ← ML detector + feature extraction
app/blockchain/ ← Web3.py Ethereum integration
app/services/   ← Email, quarantine, PDF reports
frontend/src/   ← React pages, components, stores
contracts/      ← Solidity smart contract
tests/          ← pytest unit tests
```

---

## Making changes

### Branch naming

| Type       | Branch name             |
|------------|-------------------------|
| Feature    | `feature/my-feature`    |
| Bug fix    | `fix/issue-description` |
| Docs       | `docs/update-readme`    |
| Refactor   | `refactor/cleanup-ml`   |

### Commit style (Conventional Commits)

```
feat: add IPFS storage fallback
fix: quarantine path not persisted after restart
docs: add blockchain setup instructions
test: add entropy edge case tests
refactor: simplify feature extraction loop
chore: bump scikit-learn to 1.5
```

### Code style

**Python:** Follow PEP 8. Every public function needs a docstring.
No bare `except:` — always catch specific exceptions.

**JavaScript/React:** Functional components only. Hooks for state.
Keep components under ~200 lines — split if larger.

---

## Tests

```bash
# All tests
pytest tests/ -v

# Only ML tests
pytest tests/test_detector.py -v

# Frontend build check
cd frontend && npm run build
```

All PRs must pass CI before merging. Add tests for any new functionality.

---

## Areas where help is especially welcome

- **Better ML training data** — real labelled ransomware samples improve accuracy significantly
- **IPFS integration** — completing the decentralised storage pipeline
- **WebSocket real-time scan progress** — live updates during scanning
- **More language support** — i18n for the frontend
- **More test coverage** — especially integration tests for the API routes
- **Mobile responsiveness** — the frontend works on desktop; mobile needs polish

---

## Security vulnerabilities

Please **do not** open a public GitHub issue for security vulnerabilities.
Instead, follow the process in [SECURITY.md](SECURITY.md).

---

## Licence

By contributing you agree that your contributions will be licensed under the MIT Licence.
