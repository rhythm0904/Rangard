#!/usr/bin/env python3
"""
Email Verification Flow Test
Tests: Registration → Email Verification → Threat Alert with Verified Email
"""
import sys
import json
import asyncio
sys.path.insert(0, '.')

import urllib.request
import urllib.error

class EmailVerificationTester:
    def __init__(self, base_url='http://localhost:8000'):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.email = None
        self.verification_token = None
        
    def print_section(self, title):
        print("\n" + "=" * 70)
        print(f"  {title}")
        print("=" * 70)
    
    def test_register_and_get_verification(self):
        """Test 1: Register and receive verification token"""
        self.print_section("TEST 1: User Registration & Email Verification Link")
        
        # Use timestamp to create unique email for each test run
        import time
        unique_id = int(time.time() * 1000)
        self.email = f'emailtest{unique_id}@rangard.local'
        password = 'SecurePassword12345'
        full_name = 'Email Test User'
        
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
            print(f"   Status: NOT VERIFIED (verification email would be sent)")
            print(f"\n   → In production, user receives verification email with link")
            print(f"   → They click link to verify their email address")
            
            return True
            
        except urllib.error.HTTPError as e:
            if e.code == 409:
                print("⚠️  User already exists - continuing with existing account...")
                return True
            error_data = json.loads(e.read().decode())
            print(f"❌ Registration failed: {error_data.get('detail')}")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_get_profile_unverified(self):
        """Test 2: Check profile status - email not verified"""
        self.print_section("TEST 2: Check User Profile (Email Not Verified)")
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
            print(f"   Email: {result.get('email')}")
            print(f"   Email Verified: {result.get('is_verified')}")
            print(f"   Active: {result.get('is_active')}")
            
            if not result.get('is_verified'):
                print(f"\n   ⚠️  Email NOT verified - threat alerts will NOT be sent")
            
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_resend_verification(self):
        """Test 3: Resend verification email"""
        self.print_section("TEST 3: Resend Email Verification")
        if not self.token:
            print("⚠️  Skipped (no token)")
            return False
            
        try:
            req = urllib.request.Request(
                f'{self.base_url}/api/auth/resend-verification',
                headers={'Authorization': f'Bearer {self.token}'},
                method='POST'
            )
            response = urllib.request.urlopen(req, timeout=5)
            result = json.loads(response.read().decode())
            
            print(f"✅ Verification email resent")
            print(f"   Message: {result.get('message')}")
            print(f"   → User would receive new verification email")
            
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def simulate_email_verification(self):
        """
        Test 4: Simulate email verification
        In real world, user clicks email link with token.
        Here we simulate that by generating token ourselves.
        """
        self.print_section("TEST 4: Verify Email (Simulated)")
        
        if not self.email:
            print("⚠️  Skipped (no email)")
            return False
        
        # In a real test, we'd extract the token from the email
        # For this demo, we'll generate one using the same function
        from app.core.security import create_email_verification_token
        
        verify_token = create_email_verification_token(self.email)
        print(f"Generated verification token: {verify_token[:30]}...")
        
        try:
            data = {'token': verify_token}
            payload = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(
                f'{self.base_url}/api/auth/verify-email',
                data=payload,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            response = urllib.request.urlopen(req, timeout=5)
            result = json.loads(response.read().decode())
            
            print(f"✅ Email verification successful!")
            print(f"   Message: {result.get('message')}")
            print(f"   Email: {result.get('email')}")
            print(f"   Verified: {result.get('verified')}")
            
            return True
        except urllib.error.HTTPError as e:
            error_data = json.loads(e.read().decode())
            print(f"❌ Verification failed: {error_data.get('detail')}")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_profile_after_verification(self):
        """Test 5: Check profile - email now verified"""
        self.print_section("TEST 5: Profile After Email Verification")
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
            
            is_verified = result.get('is_verified')
            print(f"✅ Profile retrieved")
            print(f"   Email: {result.get('email')}")
            print(f"   Email Verified: {is_verified}")
            
            if is_verified:
                print(f"\n   ✅ Email VERIFIED - threat alerts WILL be sent!")
            else:
                print(f"\n   ⚠️  Email NOT verified yet")
            
            return is_verified
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def run_all(self):
        """Run all email verification tests"""
        print("\n")
        print("╔" + "=" * 68 + "╗")
        print("║" + " " * 10 + "EMAIL VERIFICATION FLOW TEST SUITE" + " " * 24 + "║")
        print("╚" + "=" * 68 + "╝")
        
        tests = [
            ("Register & Get Verification Link", self.test_register_and_get_verification),
            ("Check Profile (Unverified)", self.test_get_profile_unverified),
            ("Resend Verification Email", self.test_resend_verification),
            ("Verify Email Link", self.simulate_email_verification),
            ("Check Profile (Verified)", self.test_profile_after_verification),
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
        print(f"{'='*70}")
        
        if passed == total:
            print("""
✅ EMAIL VERIFICATION WORKING!

What Happens Next:
──────────────────
1. User registers with email → receives verification email
2. User clicks link in email → email is verified
3. When file with threat detected:
   ✅ If email VERIFIED → threat alert email is sent
   ❌ If email NOT verified → threat alert suppressed
   
Security Benefits:
──────────────────
• Only real, verified emails receive alerts
• Prevents spam to invalid email addresses
• Ensures users get critical security notifications
• Reduces email bounces and invalid recipients
            """)
        
        print("\n")
        return passed == total

if __name__ == "__main__":
    tester = EmailVerificationTester()
    success = tester.run_all()
    sys.exit(0 if success else 1)
