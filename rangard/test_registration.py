#!/usr/bin/env python
"""
Test registration endpoint to diagnose the failure.
"""
import sys
sys.path.insert(0, '.')

import asyncio
import uuid
from datetime import datetime, timezone
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.models import User
from app.core.security import hash_password

async def test_registration():
    """Test the registration process."""
    print("=" * 70)
    print("REGISTRATION DIAGNOSTIC TEST")
    print("=" * 70)
    
    # Test 1: Check email service is configured
    print("\n1. Checking email service configuration...")
    try:
        from app.services.email import get_email_service
        from app.core.config import get_settings
        
        settings = get_settings()
        email_svc = get_email_service()
        
        print(f"   ✓ Email service loaded")
        print(f"   ✓ Gmail user: {email_svc.gmail_user}")
        print(f"   ✓ SMTP server: {email_svc.smtp_server}:{email_svc.smtp_port}")
        print(f"   ✓ App env: {settings.APP_ENV}")
        
        if not email_svc.gmail_user:
            print("   ❌ Gmail email not configured!")
            return False
            
        if not email_svc.gmail_password:
            print("   ❌ Gmail password not configured!")
            return False
            
    except Exception as e:
        print(f"   ❌ Error loading email service: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Try to create a user in database
    print("\n2. Testing user creation in database...")
    test_email = f"test_registration_{uuid.uuid4().hex[:8]}@test.com"
    test_password = "TestPassword123"
    
    try:
        async with AsyncSessionLocal() as session:
            # Check if user already exists
            result = await session.execute(select(User).where(User.email == test_email))
            existing = result.scalar_one_or_none()
            
            if existing:
                print(f"   ⚠️  User already exists: {test_email}")
            else:
                # Create new user
                new_user = User(
                    email=test_email,
                    hashed_password=hash_password(test_password),
                    full_name="Test User",
                    is_active=True,
                    is_verified=False,
                )
                session.add(new_user)
                await session.commit()
                await session.refresh(new_user)
                print(f"   ✓ User created: {test_email}")
                print(f"   ✓ User ID: {new_user.id}")
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Try to send verification email
    print("\n3. Testing verification email sending...")
    try:
        verification_link = f"http://localhost:3000/verify-email?token=test_token_12345"
        success, error_msg = email_svc.send_email_verification(test_email, verification_link)
        
        if success:
            print(f"   ✓ Email sent successfully to {test_email}")
        else:
            print(f"   ❌ Email sending failed: {error_msg}")
            return False
            
    except Exception as e:
        print(f"   ❌ Email service error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED - Registration should work!")
    print("=" * 70)
    return True

if __name__ == "__main__":
    result = asyncio.run(test_registration())
    sys.exit(0 if result else 1)
