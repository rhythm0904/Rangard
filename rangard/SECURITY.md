# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 1.x     | ✅ Yes     |

## Reporting a vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

If you believe you've found a security vulnerability in RANGARD, please send an email to:

**security@rangard.app**

Include:
- A description of the vulnerability
- Steps to reproduce
- Potential impact
- Any suggested fixes (optional)

You will receive an acknowledgement within **48 hours** and a full response within **7 days**.

We ask that you:
- Give us reasonable time to fix the issue before public disclosure
- Not access or modify other users' data
- Not perform denial-of-service attacks

We appreciate responsible disclosure and will credit researchers in the release notes (unless you prefer anonymity).

## Security considerations for self-hosters

### Never commit these to git
- `.env` file
- `WALLET_PRIVATE_KEY`
- `SENDGRID_API_KEY`
- JWT `SECRET_KEY`
- Any `*.pem` or `*.key` files

### Production hardening checklist
- [ ] Set `APP_ENV=production`
- [ ] Use a strong random `SECRET_KEY` (32+ bytes): `openssl rand -hex 32`
- [ ] Enable HTTPS / SSL (see `nginx/rangard.conf`)
- [ ] Set `ALLOWED_ORIGINS` to your exact frontend domain
- [ ] Use a dedicated low-privilege database user
- [ ] Enable PostgreSQL SSL connections
- [ ] Store `WALLET_PRIVATE_KEY` in a secrets manager (AWS Secrets Manager, Vault)
- [ ] Keep Docker images up to date
- [ ] Enable rate limiting (already in `app/main.py` via slowapi — configure limits)
- [ ] Review quarantine directory permissions (`chmod 700 /var/rangard/quarantine`)
