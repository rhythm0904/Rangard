#!/usr/bin/env python3
import sys
import json
import base64
sys.path.insert(0, '.')

import urllib.request
import urllib.error

def test_file_upload():
    """Test file upload and scanning"""
    print("=" * 60)
    print("Testing File Upload and Scanning")
    print("=" * 60)
    
    # First, register and get a token
    print("\n1. Registering user...")
    data = {
        'email': 'scanner@test.com',
        'password': 'TestPassword123',
        'full_name': 'Scanner User'
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
        token = result.get('access_token')
        print(f"   ✅ User registered: {result.get('email')}")
    except urllib.error.HTTPError as e:
        if e.code == 409:
            # User already exists, try to login
            print("   User already exists, trying login...")
            # For now, just use a test token
            token = None
        else:
            error_data = json.loads(e.read().decode())
            print(f"   ❌ Error: {error_data.get('detail')}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    if not token:
        print("   ❌ Could not get token")
        return False
    
    # Create a test file (with high entropy to be detected as potentially malicious)
    print("\n2. Creating test file with high entropy...")
    test_content = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f' * 100  # Random-looking bytes
    
    # Create multipart form data
    boundary = '----WebKitFormBoundary'
    body = b''
    body += f'--{boundary}\r\n'.encode()
    body += b'Content-Disposition: form-data; name="file"; filename="testfile.bin"\r\n'
    body += b'Content-Type: application/octet-stream\r\n\r\n'
    body += test_content
    body += f'\r\n--{boundary}--\r\n'.encode()
    
    print("   ✅ Test file created")
    
    # Upload and scan
    print("\n3. Uploading file for scanning...")
    try:
        req = urllib.request.Request(
            'http://localhost:8000/api/scans/upload',
            data=body,
            headers={
                'Content-Type': f'multipart/form-data; boundary={boundary}',
                'Authorization': f'Bearer {token}'
            },
            method='POST'
        )
        
        response = urllib.request.urlopen(req, timeout=30)
        scan_result = json.loads(response.read().decode())
        
        print(f"   ✅ Scan completed!")
        print(f"\n   Scan Results:")
        print(f"     - Threat Level: {scan_result.get('threat_level')}")
        print(f"     - Confidence: {scan_result.get('confidence')}")
        print(f"     - Quarantined: {scan_result.get('quarantined')}")
        print(f"     - Scan ID: {scan_result.get('scan_id')}")
        print(f"     - Message: {scan_result.get('message')}")
        
        if scan_result.get('threat_level') != 'clean':
            print(f"\n   ✅ Real analysis working! Detected threat: {scan_result.get('threat_level')}")
        else:
            print(f"\n   ⚠️  Scan detected as clean")
        
        return True
        
    except urllib.error.HTTPError as e:
        print(f"   ❌ Error: {e.code}")
        error_data = json.loads(e.read().decode())
        print(f"   Detail: {error_data.get('detail')}")
        return False
        
    except Exception as e:
        print(f"   ❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_file_upload()
    sys.exit(0 if success else 1)
