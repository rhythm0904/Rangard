#!/usr/bin/env python3
"""Test the full email alert workflow."""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

print("="*60)
print("Testing Email Alert Workflow")
print("="*60)

# 1. Register a user
print("\n1. Registering user...")
register_resp = requests.post(
    f"{BASE_URL}/auth/register",
    json={
        "email": "test.email.rangard+flow@gmail.com",
        "password": "TestPass123!",
        "full_name": "Test User Flow"
    }
)

if register_resp.status_code == 201:
    user_data = register_resp.json()
    user_id = user_data.get("id")
    token = user_data.get("access_token")
    is_verified = user_data.get("is_email_verified")
    print(f"   ✅ User registered: {user_id}")
    print(f"   - Email verified: {is_verified}")
    print(f"   - Token: {token[:20]}...")
else:
    print(f"   ❌ Registration failed: {register_resp.status_code}")
    print(f"   Response: {register_resp.text}")
    exit(1)

# 2. Create a test file with content that triggers detection
print("\n2. Creating test file with suspicious content...")
suspicious_content = b"This is a test file with suspicious patterns for ransomware detection: LOCKED_FILE ENCRYPTED_DATA RANSOM"

# 3. Upload the file to trigger threat detection
print("\n3. Uploading file for threat detection...")
headers = {
    "Authorization": f"Bearer {token}"
}

files = {
    "file": ("suspicious.txt", suspicious_content, "text/plain")
}

upload_resp = requests.post(
    f"{BASE_URL}/scans/upload",
    files=files,
    headers=headers
)

if upload_resp.status_code == 200:
    scan_data = upload_resp.json()
    print(f"   ✅ File scanned:")
    print(f"   - Scan ID: {scan_data.get('scan_id')}")
    print(f"   - Status: {scan_data.get('status')}")
    print(f"   - Threat Level: {scan_data.get('threat_level')}")
    print(f"   - Quarantined: {scan_data.get('quarantined')}")
    print(f"   - Message: {scan_data.get('message')}")
    
    if scan_data.get('threat_level') != 'clean':
        print("\n   📧 Email Alert Status:")
        if is_verified:
            print(f"   ✅ Threat alert SHOULD be sent (user verified)")
        else:
            print(f"   ⏳ Threat alert NOT sent (user not verified)")
else:
    print(f"   ❌ Upload failed: {upload_resp.status_code}")
    print(f"   Response: {upload_resp.text}")

print("\n" + "="*60)
print("Check test.email.rangard+flow@gmail.com for the alert email!")
print("="*60)
