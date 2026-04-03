#!/usr/bin/env python3
"""Test registration and login endpoints."""
import sys
import json
import time
import urllib.request
import urllib.error

BASE_URL = "http://localhost:8000"

def test_register():
    """Test user registration."""
    print("\n1. Testing Registration")
    print("=" * 60)
    
    data = {
        "email": f"testuser{int(time.time())}@example.com",
        "password": "TestPassword123",
        "full_name": "Test User"
    }
    
    try:
        payload = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(
            f'{BASE_URL}/api/auth/register',
            data=payload,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        response = urllib.request.urlopen(req, timeout=5)
        result = json.loads(response.read().decode())
        
        print(f"✅ Registration successful!")
        print(f"   Email: {result.get('email')}")
        print(f"   Token: {result.get('access_token')[:40]}...")
        print(f"   User ID: {result.get('user_id')}")
        
        return result.get('access_token'), result.get('email')
        
    except urllib.error.HTTPError as e:
        error_data = json.loads(e.read().decode())
        print(f"❌ Registration failed (HTTP {e.code})")
        print(f"   Error: {error_data.get('detail')}")
        return None, None
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return None, None


def test_login(email):
    """Test user login."""
    print("\n2. Testing Login")
    print("=" * 60)
    
    data = {
        "username": email,
        "password": "TestPassword123"
    }
    
    try:
        payload = urllib.parse.urlencode(data).encode('utf-8')
        req = urllib.request.Request(
            f'{BASE_URL}/api/auth/login',
            data=payload,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            method='POST'
        )
        
        response = urllib.request.urlopen(req, timeout=5)
        result = json.loads(response.read().decode())
        
        print(f"✅ Login successful!")
        print(f"   Email: {result.get('email')}")
        print(f"   Token: {result.get('access_token')[:40]}...")
        print(f"   Token Type: {result.get('token_type')}")
        
        return result.get('access_token')
        
    except urllib.error.HTTPError as e:
        error_data = json.loads(e.read().decode())
        print(f"❌ Login failed (HTTP {e.code})")
        print(f"   Error: {error_data.get('detail')}")
        return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None


def test_get_me(token):
    """Test getting current user info."""
    print("\n3. Testing Get Current User")
    print("=" * 60)
    
    try:
        req = urllib.request.Request(
            f'{BASE_URL}/api/auth/me',
            headers={'Authorization': f'Bearer {token}'},
            method='GET'
        )
        
        response = urllib.request.urlopen(req, timeout=5)
        result = json.loads(response.read().decode())
        
        print(f"✅ Get user successful!")
        print(f"   ID: {result.get('id')}")
        print(f"   Email: {result.get('email')}")
        print(f"   Full Name: {result.get('full_name')}")
        print(f"   Is Verified: {result.get('is_verified')}")
        print(f"   Is Active: {result.get('is_active')}")
        
        return True
        
    except urllib.error.HTTPError as e:
        error_data = json.loads(e.read().decode())
        print(f"❌ Get user failed (HTTP {e.code})")
        print(f"   Error: {error_data.get('detail')}")
        return False
    except Exception as e:
        print(f"❌ Get user error: {e}")
        return False


def main():
    print("\n" + "=" * 60)
    print("RANGARD Authentication Test Suite")
    print("=" * 60)
    
    # Wait for server to be ready
    print("\nWaiting for server to be ready...")
    for i in range(30):
        try:
            urllib.request.urlopen(f"{BASE_URL}/docs", timeout=1)
            print("✅ Server is ready!\n")
            break
        except:
            time.sleep(0.5)
            if i % 5 == 0:
                print(f"  Still waiting... ({i}s)")
    
    # Test registration
    token, email = test_register()
    if not token:
        print("\n❌ Registration failed - stopping tests")
        return 1
    
    # Test login
    login_token = test_login(email)
    if not login_token:
        print("\n❌ Login failed")
        return 1
    
    # Test get me
    if not test_get_me(login_token):
        print("\n❌ Get user failed")
        return 1
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    import urllib.parse
    sys.exit(main())
