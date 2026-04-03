#!/usr/bin/env python3
import sys
import json
sys.path.insert(0, '.')

# Test registration via HTTP
import urllib.request
import urllib.error

def test_registration():
    print("=" * 60)
    print("Testing Registration Endpoint")
    print("=" * 60)
    
    # Test data
    data = {
        'email': 'newuser123@test.com',
        'password': 'TestPassword123',
        'full_name': 'New Test User'
    }
    
    try:
        payload = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(
            'http://localhost:8000/api/auth/register',
            data=payload,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        response = urllib.request.urlopen(req, timeout=5)
        result = json.loads(response.read().decode())
        
        print(f"SUCCESS! Status: {response.status}")
        print(f"\nResponse:")
        print(f"  - user_id: {result.get('user_id')}")
        print(f"  - email: {result.get('email')}")
        print(f"  - token_type: {result.get('token_type')}")
        print(f"  - access_token: {result.get('access_token')[:30]}...")
        
        return True
        
    except urllib.error.HTTPError as e:
        print(f"ERROR! Status: {e.code}")
        error_data = json.loads(e.read().decode())
        print(f"Detail: {error_data.get('detail')}")
        return False
        
    except Exception as e:
        print(f"ERROR! {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_registration()
    sys.exit(0 if success else 1)
