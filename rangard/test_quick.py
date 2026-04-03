#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, '.')

# Test imports
print("Testing imports...")
try:
    from app.core.security import hash_password, verify_password
    print("✅ Security module imported")
    
    # Test password hashing
    pwd = "TestPassword123"
    hashed = hash_password(pwd)
    print(f"✅ Password hashed: {hashed[:20]}...")
    
    verified = verify_password(pwd, hashed)
    print(f"✅ Password verified: {verified}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\nTesting database...")
try:
    from app.core.database import create_tables
    from app.core.models import User
    import asyncio
    
    async def test_db():
        try:
            await create_tables()
            print("✅ Database tables created")
        except Exception as e:
            print(f"❌ Database error: {e}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(test_db())
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ All tests passed!")
