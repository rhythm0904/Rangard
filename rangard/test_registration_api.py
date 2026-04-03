#!/usr/bin/env python3
import sys
import asyncio
sys.path.insert(0, '.')

async def test_registration():
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
    from app.core.models import Base, User
    from app.core.security import hash_password, create_access_token
    from app.core.config import get_settings
    
    settings = get_settings()
    
    # Create an async engine specifically for testing
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as db:
        try:
            # Simulate registration
            email = "testuser@example.com"
            password = "TestPassword123"
            full_name = "Test User"
            
            # Check if user already exists
            from sqlalchemy import select
            result = await db.execute(select(User).where(User.email == email))
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print(f"⚠️  User already exists: {existing_user.email}")
                # Delete for testing
                await db.delete(existing_user)
                await db.commit()
                print("   Deleted existing user for testing")
            
            # Hash password
            hashed_password = hash_password(password)
            
            # Create new user
            new_user = User(
                email=email,
                hashed_password=hashed_password,
                full_name=full_name or "",
                is_active=True,
            )
            
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            
            print(f"✅ User created successfully!")
            print(f"   ID: {new_user.id}")
            print(f"   Email: {new_user.email}")
            print(f"   Full Name: {new_user.full_name}")
            
            # Generate token
            token = create_access_token(str(new_user.id))
            print(f"✅ JWT Token created: {token[:30]}...")
            
            print("\n✅ Registration test PASSED!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

asyncio.run(test_registration())
