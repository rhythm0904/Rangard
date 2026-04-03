# 🛡️ RANGARD

**Stop ransomware before it strikes.**

[![CI](https://github.com/rhythm0904/rangard/actions/workflows/ci.yml/badge.svg)](https://github.com/rhythm0904/rangard/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-violet.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![React 18](https://img.shields.io/badge/React-18-61dafb.svg)](https://react.dev)
[![Ethereum](https://img.shields.io/badge/Ethereum-Sepolia-627eea.svg)](https://sepolia.etherscan.io)

RANGARD is an AI-powered ransomware detection platform. Upload any file — our ML model analyses 14 behavioural features in under 50ms, quarantines threats instantly, anchors clean file hashes to Ethereum, and fires a ThreatPulse email alert the moment danger is detected.

---

## ✨ Features

| | Feature | |
|---|---|---|
| 🧠 | **AI Behavioural Analysis** | RandomForest model, 14 features, catches zero-day ransomware |
| ⛓️ | **Blockchain File Proof** | SHA-256 anchored to Ethereum — immutable, verifiable forever |
| 🔒 | **Instant Quarantine** | Fernet-encrypted isolation in milliseconds |
| 📡 | **ThreatPulse** | Instant styled email alert via SendGrid on every threat |
| 🎯 | **Live Scan Results** | Animated confidence ring, pattern list, blockchain TX |

---

## 🚀 Quick start

```bash
git clone https://github.com/rhythm0904/rangard.git
cd rangard
bash scripts/setup.sh
```

**API docs:** http://localhost:8000/docs  
**Frontend:** http://localhost:3000

---

## 🏗️ Architecture

```
frontend/          React + Vite + Framer Motion + Recharts (Vercel)
app/
  api/             FastAPI routes (auth, scans)
  core/            Config, DB models, JWT security
  ml/              RandomForest ransomware detector
  blockchain/      Web3.py + Infura Ethereum integration  
  services/        ThreatPulse email, quarantine, PDF reports
contracts/         Solidity FileRegistry smart contract
tests/             pytest unit tests
docs/              Full deployment guide
scripts/           setup.sh, train_model.py
```

---

## 🧠 How detection works

```
File bytes → 14 features extracted:
  entropy_full     High = likely encrypted = ransomware signal
  ransom_strings   "bitcoin", "decrypt", ".onion" hits
  pe_suspicious    Unusual PE headers or section count  
  null_byte_ratio  High = encrypted payload
  ...and 9 more

→ RandomForest (100 trees) → probability 0.0–1.0

< 15%  CLEAN   ✅    < 35%  LOW     ⚠️
< 55%  MEDIUM  🚨    < 75%  HIGH    🚨    ≥ 75%  CRITICAL  🔴
```

---

## 🤝 Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md). PRs welcome.

## 📜 License

MIT — see [LICENSE](LICENSE)

## 🔒 Security

Report vulnerabilities to security@rangard.app — do not open public issues.

---

<p align="center">Built by <a href="https://github.com/rhythm0904">rhythm0904</a> · Python · FastAPI · React · scikit-learn · Ethereum</p>
