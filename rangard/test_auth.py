import sys
sys.path.insert(0, '.')

import requests
import json

# Test health endpoint
try:
    r = requests.get('http://localhost:8000/health', timeout=2)
    print(f"Health: {r.status_code} - {r.text}")
except Exception as e:
    print(f"Health check failed: {e}")

# Test register endpoint
try:
    r = requests.post(
        'http://localhost:8000/api/auth/register',
        json={
            'email': 'test@example.com',
            'password': 'Test12345',
            'full_name': 'Test User'
        },
        timeout=5
    )
    print(f"Register: {r.status_code}")
    print(f"Response: {json.dumps(r.json(), indent=2)}")
except Exception as e:
    print(f"Register failed: {e}")
