import sys
sys.path.insert(0, '.')

import urllib.request
import json

# Test health endpoint  
try:
    req = urllib.request.urlopen('http://localhost:8000/health')
    response = req.read()
    print(f"Health: 200")
    print(f"Response: {response.decode()}")
except Exception as e:
    print(f"Health failed: {e}")

# Test register endpoint
try:
    data = json.dumps({
        'email': 'test@example.com',
        'password': 'Test12345',
        'full_name': 'Test User'
    }).encode('utf-8')
    
    req = urllib.request.Request(
        'http://localhost:8000/api/auth/register',
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    
    response = urllib.request.urlopen(req)
    result = response.read().decode()
    print(f"Register: {response.status}")
    print(f"Response: {result}")
except urllib.error.HTTPError as e:
    error_response = e.read().decode()
    print(f"Register failed: {e.code} - {error_response}")
except Exception as e:
    print(f"Register error: {e}")
