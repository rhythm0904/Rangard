#!/usr/bin/env python3
"""Quick test to diagnose registration/login issues."""
import sys
sys.path.insert(0, '.')

import asyncio
from app.core.database import get_db, init_db
from app.core.security import hash_password, create_access_token
from app.core.models import User

async def test_auth():
    print("Testing authentication components...\n")
    
    # Test 1: Check database
    print("1. Database Connection")
    try:
        await init_db()
        print("   ✅ Database initialized")
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return
    
    # Test 2: Hash password
    print("\n2. Password Hashing")
    try:
        password = "TestPassword123"
        hashed = hash_password(password)
        print(f"   ✅ Password hashed successfully")
        print(f"      Hash: {hashed[:40]}...")
    except Exception as e:
        print(f"   ❌ Hash error: {e}")
        return
    
    # Test 3: Create JWT token
    print("\n3. JWT Token Creation")
    try:
        token = create_access_token("test-user-123")
        print(f"   ✅ Token created successfully")
        print(f"      Token: {token[:40]}...")
    except Exception as e:
        print(f"   ❌ Token error: {e}")
        return
    
    print("\n✅ All components working!")

if __name__ == "__main__":
    asyncio.run(test_auth())
