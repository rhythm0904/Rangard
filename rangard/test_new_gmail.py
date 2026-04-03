#!/usr/bin/env python
"""Test email sending with new Gmail address"""
import requests
import time

BASE_URL = 'http://localhost:8000'
test_email = f'verify.test.{int(time.time())}@gmail.com'
password = 'TestPass123!'

print('🧪 Testing Email from rangard.safe@gmail.com')
print('=' * 70)

# Step 1: Register user
print(f'\n1️⃣  Registering user')
print(f'   Email: {test_email}')
print(f'   Password: {password}')

r = requests.post(f'{BASE_URL}/api/auth/register', json={
    'email': test_email,
    'password': password,
    'full_name': 'Test User'
})

print(f'   Status: {r.status_code}')

if r.status_code != 200:
    print(f'   ❌ Failed: {r.text}')
    exit(1)

token = r.json()['access_token']
print(f'   ✅ User registered!')

# Step 2: Send verification email
print(f'\n2️⃣  Sending verification email')

r = requests.post(
    f'{BASE_URL}/api/auth/resend-verification',
    headers={'Authorization': f'Bearer {token}'}
)

print(f'   Status: {r.status_code}')
print(f'   Response: {r.json()}')

if r.status_code == 200:
    print(f'   ✅ Email sent SUCCESSFULLY!')
    print(f'   From: rangard.safe@gmail.com')
    print(f'   To: {test_email}')
    print(f'\n📧 CHECK YOUR INBOX at: {test_email}')
    print(f'   (Emails arrive in 5-10 seconds)')
else:
    print(f'   ❌ Error sending email')
    print(f'   Full response: {r.text}')

print('\n' + '=' * 70)
