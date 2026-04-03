#!/usr/bin/env python3
"""Quick test of email verification endpoints"""
import urllib.request
import json

def test_endpoint(url, data=None, headers=None):
    """Test a single endpoint"""
    if headers is None:
        headers = {}
    
    try:
        if data:
            payload = json.dumps(data).encode('utf-8')
            headers['Content-Type'] = 'application/json'
            req = urllib.request.Request(url, data=payload, headers=headers, method='POST')
        else:
            req = urllib.request.Request(url, headers=headers, method='GET')
        
        response = urllib.request.urlopen(req, timeout=2)
        result = json.loads(response.read().decode())
        return True, response.status, result
    except urllib.error.HTTPError as e:
        try:
            error_data = json.loads(e.read().decode())
            return False, e.code, error_data.get('detail', str(error_data))
        except:
            return False, e.code, e.reason
    except Exception as e:
        return False, None, str(e)

print("Testing Email Verification Endpoints")
print("=" * 60)

# Test verify-email endpoint
print("\n1. Testing /api/auth/verify-email...")
success, status, response = test_endpoint(
    'http://localhost:8000/api/auth/verify-email',
    {'token': 'invalid-token'}
)
print(f"   Status: {status}")
print(f"   Response: {response}")

# Test resend-verification endpoint  
print("\n2. Testing /api/auth/resend-verification...")
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0In0.test"
success, status, response = test_endpoint(
    'http://localhost:8000/api/auth/resend-verification',
    headers={'Authorization': f'Bearer {token}'}
)
print(f"   Status: {status}")
print(f"   Response: {response}")

print("\n" + "=" * 60)
if status in [200, 400, 401, 404, 500]:
    print("✅ Endpoints are reachable")
else:
    print(f"⚠️  Unexpected status: {status}")
