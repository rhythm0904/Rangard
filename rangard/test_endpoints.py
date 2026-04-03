#!/usr/bin/env python3
import urllib.request
import json

# Test if the new endpoints exist by checking API documentation
try:
    print("Checking if email verification endpoints are registered...")
    req = urllib.request.Request(
        'http://localhost:8000/docs',
        headers={'Accept': 'text/html'},
        method='GET'
    )
    response = urllib.request.urlopen(req, timeout=5)
    content = response.read().decode()
    
    # Look for the endpoint in the OpenAPI docs
    if '/api/auth/verify-email' in content:
        print("✅ /api/auth/verify-email endpoint is registered")
    else:
        print("❌ /api/auth/verify-email endpoint NOT found in docs")
    
    if '/api/auth/resend-verification' in content:
        print("✅ /api/auth/resend-verification endpoint is registered")
    else:
        print("❌ /api/auth/resend-verification endpoint NOT found in docs")
        
except Exception as e:
    print(f"Could not check: {e}")

# Try calling the verify-email endpoint directly with a test token
print("\nTesting verify-email endpoint...")
try:
    data = {'token': 'test-token-123'}
    payload = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(
        'http://localhost:8000/api/auth/verify-email',
        data=payload,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    response = urllib.request.urlopen(req, timeout=5)
    result = json.loads(response.read().decode())
    print(f"✅ Response: {result}")
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.reason}")
    try:
        error_data = json.loads(e.read().decode())
        print(f"   Detail: {error_data.get('detail')}")
    except:
        print(f"   Could not parse error response")
except Exception as e:
    print(f"Error: {e}")
