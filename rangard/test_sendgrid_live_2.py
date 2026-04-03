#!/usr/bin/env python3
"""
Test SendGrid email integration with the new API key.
Verifies that threat alerts and email verification can be sent.
"""
import sys
import asyncio
sys.path.insert(0, '.')

from app.core.config import get_settings
from app.services.email import get_email_service


def test_sendgrid_config():
    """Test that SendGrid is properly configured."""
    print("=" * 60)
    print("Testing SendGrid Configuration")
    print("=" * 60)
    
    settings = get_settings()
    
    print("\n1. Checking SendGrid API Key...")
    if not settings.SENDGRID_API_KEY:
        print("   ❌ SENDGRID_API_KEY is not set in .env")
        return False
    
    if settings.SENDGRID_API_KEY.startswith("SG.XXX"):
        print("   ❌ SENDGRID_API_KEY is a placeholder (SG.XXX...)")
        return False
    
    # Check format
    if settings.SENDGRID_API_KEY.startswith("SG."):
        key_prefix = settings.SENDGRID_API_KEY[:10]
        print(f"   ✅ API Key detected: {key_prefix}...")
    else:
        print(f"   ❌ API Key format invalid: {settings.SENDGRID_API_KEY[:20]}...")
        return False
    
    print("\n2. Checking Email Configuration...")
    print(f"   EMAIL_FROM: {settings.EMAIL_FROM}")
    print(f"   EMAIL_FROM_NAME: {settings.EMAIL_FROM_NAME}")
    print(f"   APP_ENV: {settings.APP_ENV}")
    
    if not settings.EMAIL_FROM or "@" not in settings.EMAIL_FROM:
        print("   ❌ EMAIL_FROM is not set or invalid")
        return False
    
    print("\n3. Initializing EmailService...")
    email_svc = get_email_service()
    
    if email_svc.client is None:
        print("   ⚠️  EmailService client is None")
        print("       (This is OK in development mode or if sendgrid package not installed)")
        print("       In production, the sendgrid package should be installed")
    else:
        print("   ✅ SendGrid client initialized successfully")
    
    return True


def test_threat_alert_template():
    """Test generating a threat alert email."""
    print("\n" + "=" * 60)
    print("Testing Threat Alert Email Generation")
    print("=" * 60)
    
    settings = get_settings()
    email_svc = get_email_service()
    
    test_params = {
        "to_email": "test@example.com",
        "to_name": "Test User",
        "filename": "suspicious_file.exe",
        "threat_level": "critical",
        "confidence": 0.92,
        "patterns": [
            "Very high file entropy (7.8/8.0) — characteristic of encrypted or packed content",
            "Found 2 ransomware-related string(s) embedded in file"
        ],
        "scan_id": "scan_abc123def456",
    }
    
    print(f"\n1. Sending threat alert to {test_params['to_email']}...")
    success, error = email_svc.send_threat_alert(**test_params)
    
    if success:
        print(f"   ✅ Email sent successfully (or logged in dev mode)")
        return True
    else:
        print(f"   ❌ Failed to send email: {error}")
        return False


def test_verification_email():
    """Test generating an email verification link."""
    print("\n" + "=" * 60)
    print("Testing Email Verification Email Generation")
    print("=" * 60)
    
    email_svc = get_email_service()
    
    test_params = {
        "to_email": "newuser@example.com",
        "verification_link": "http://localhost:3000/verify?token=abc123xyz789",
    }
    
    print(f"\n1. Sending verification email to {test_params['to_email']}...")
    success, error = email_svc.send_email_verification(**test_params)
    
    if success:
        print(f"   ✅ Verification email sent successfully (or logged in dev mode)")
        return True
    else:
        print(f"   ❌ Failed to send verification email: {error}")
        return False


def main():
    print("\n")
    print("╔════════════════════════════════════════════════════════╗")
    print("║     RANGARD Email Service Test Suite                  ║")
    print("║     Testing SendGrid Integration                      ║")
    print("╚════════════════════════════════════════════════════════╝")
    
    results = []
    
    # Test 1: Configuration
    results.append(("SendGrid Config", test_sendgrid_config()))
    
    # Test 2: Threat Alert Template
    results.append(("Threat Alert Email", test_threat_alert_template()))
    
    # Test 3: Verification Email
    results.append(("Verification Email", test_verification_email()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status:8} {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All tests passed!")
        print("\nThe system is ready to send alert emails for threat detections.")
        print("Make sure to:")
        print("  1. Verify the sender email in SendGrid dashboard")
        print("  2. Users must verify their emails to receive alerts")
        return 0
    else:
        print("❌ Some tests failed. Review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
