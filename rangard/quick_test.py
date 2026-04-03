#!/usr/bin/env python3
"""Quick test of SendGrid setup."""
from app.core.config import get_settings
from app.services.email import get_email_service

settings = get_settings()
print('✅ Configuration Loaded')
print(f'EMAIL_FROM: {settings.EMAIL_FROM}')
print(f'EMAIL_FROM_NAME: {settings.EMAIL_FROM_NAME}')
print(f'API Key: {settings.SENDGRID_API_KEY[:20]}...')

email_svc = get_email_service()
print(f'✅ EmailService initialized')
print(f'SendGrid client connected: {email_svc.client is not None}')
