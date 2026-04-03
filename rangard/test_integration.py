#!/usr/bin/env python3
"""
Comprehensive Integration Test for RANGARD
Tests: Registration → Login → File Upload → Scan Analysis
"""
import sys
import json
sys.path.insert(0, '.')

import urllib.request
import urllib.error

class RangardTester:
    def __init__(self, base_url='http://localhost:8000'):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.email = None
        
    def print_section(self, title):
        print("\n" + "=" * 70)
        print(f"  {title}")
        print("=" * 70)
    
    def test_health(self):
        """Test 1: Health Check"""
        self.print_section("TEST 1: Health Check")
        try:
            req = urllib.request.urlopen(f'{self.base_url}/health', timeout=5)
            data = json.loads(req.read().decode())
            print(f"✅ Server is running")
            print(f"   Service: {data.get('service')}")
            print(f"   Version: {data.get('version')}")
            return True
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False
    
    def test_register(self):
        """Test 2: User Registration"""
        self.print_section("TEST 2: User Registration")
        self.email = 'integration_test@rangard.local'
        password = 'TestPassword12345'
        full_name = 'Integration Tester'
        
        try:
            data = {
                'email': self.email,
                'password': password,
                'full_name': full_name
            }
            payload = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(
                f'{self.base_url}/api/auth/register',
                data=payload,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            response = urllib.request.urlopen(req, timeout=5)
            result = json.loads(response.read().decode())
            
            self.token = result.get('access_token')
            self.user_id = result.get('user_id')
            
            print(f"✅ Registration successful")
            print(f"   Email: {result.get('email')}")
            print(f"   User ID: {self.user_id}")
            print(f"   Token: {self.token[:30]}...")
            return True
            
        except urllib.error.HTTPError as e:
            if e.code == 409:
                print("⚠️  User already exists - using for login test")
                self.test_login_existing()
                return True
            error_data = json.loads(e.read().decode())
            print(f"❌ Registration failed: {error_data.get('detail')}")
            return False
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False
    
    def test_login_existing(self):
        """Login if user already exists"""
        self.print_section("TEST 2b: User Login (Existing User)")
        password = 'TestPassword12345'
        
        try:
            from io import BytesIO
            import urllib.parse
            
            data = urllib.parse.urlencode({
                'username': self.email,
                'password': password
            }).encode('utf-8')
            
            req = urllib.request.Request(
                f'{self.base_url}/api/auth/login',
                data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                method='POST'
            )
            response = urllib.request.urlopen(req, timeout=5)
            result = json.loads(response.read().decode())
            
            self.token = result.get('access_token')
            self.user_id = result.get('user_id')
            
            print(f"✅ Login successful")
            print(f"   Email: {result.get('email')}")
            print(f"   Token: {self.token[:30]}...")
            
        except Exception as e:
            print(f"❌ Login failed: {e}")
    
    def test_get_profile(self):
        """Test 3: Get User Profile"""
        self.print_section("TEST 3: Get User Profile")
        if not self.token:
            print("⚠️  Skipped (no token)")
            return False
            
        try:
            req = urllib.request.Request(
                f'{self.base_url}/api/auth/me',
                headers={'Authorization': f'Bearer {self.token}'},
                method='GET'
            )
            response = urllib.request.urlopen(req, timeout=5)
            result = json.loads(response.read().decode())
            
            print(f"✅ Profile retrieved")
            print(f"   User ID: {result.get('id')}")
            print(f"   Email: {result.get('email')}")
            print(f"   Full Name: {result.get('full_name')}")
            print(f"   Active: {result.get('is_active')}")
            return True
        except Exception as e:
            print(f"❌ Profile retrieval failed: {e}")
            return False
    
    def test_file_scan(self):
        """Test 4: File Upload and Scan"""
        self.print_section("TEST 4: File Upload and Scanning")
        if not self.token:
            print("⚠️  Skipped (no token)")
            return False
        
        try:
            # Create a test file with patterns that might trigger analysis
            test_content = b'MZ' + b'\x90' * 100  # PE header + NOP sled
            
            # Create multipart form data
            boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
            body = b''
            body += f'--{boundary}\r\n'.encode()
            body += b'Content-Disposition: form-data; name="file"; filename="test.exe"\r\n'
            body += b'Content-Type: application/octet-stream\r\n\r\n'
            body += test_content
            body += f'\r\n--{boundary}--\r\n'.encode()
            
            req = urllib.request.Request(
                f'{self.base_url}/api/scans/upload',
                data=body,
                headers={
                    'Content-Type': f'multipart/form-data; boundary={boundary}',
                    'Authorization': f'Bearer {self.token}'
                },
                method='POST'
            )
            
            response = urllib.request.urlopen(req, timeout=30)
            result = json.loads(response.read().decode())
            
            print(f"✅ File scanned successfully")
            print(f"   Scan ID: {result.get('scan_id')}")
            print(f"   Threat Level: {result.get('threat_level')}")
            print(f"   Confidence: {result.get('confidence')}")
            print(f"   Quarantined: {result.get('quarantined')}")
            print(f"   Message: {result.get('message')}")
            print(f"\n   ✅ REAL ANALYSIS in progress!")
            return True
            
        except Exception as e:
            print(f"❌ Scan failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_all(self):
        """Run all tests"""
        print("\n")
        print("╔" + "=" * 68 + "╗")
        print("║" + " " * 15 + "RANGARD Integration Test Suite" + " " * 23 + "║")
        print("╚" + "=" * 68 + "╝")
        
        tests = [
            ("Health Check", self.test_health),
            ("Registration", self.test_register),
            ("Get Profile", self.test_get_profile),
            ("File Scanning", self.test_file_scan),
        ]
        
        results = []
        for name, test_func in tests:
            try:
                result = test_func()
                results.append((name, result))
            except Exception as e:
                print(f"\n❌ Unexpected error in {name}: {e}")
                results.append((name, False))
        
        # Summary
        self.print_section("TEST SUMMARY")
        passed = sum(1 for _, r in results if r)
        total = len(results)
        
        for name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}  {name}")
        
        print(f"\n{'='*70}")
        print(f"Results: {passed}/{total} passed")
        print(f"{'='*70}\n")
        
        return passed == total

if __name__ == "__main__":
    tester = RangardTester()
    success = tester.run_all()
    sys.exit(0 if success else 1)
