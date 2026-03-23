import asyncio
import sys
sys.path.insert(0, '.')

async def test():
    from app.core.database import AsyncSessionLocal
    from app.core.models import User
    from app.core.security import hash_password
    import uuid
    
    async with AsyncSessionLocal() as db:
        try:
            user = User(
                id=str(uuid.uuid4()),
                email="test@test.com",
                hashed_password=hash_password("password123"),
                full_name="Test User"
            )
            db.add(user)
            await db.commit()
            print("SUCCESS! User created!")
        except Exception as e:
            print(f"ERROR: {e}")

asyncio.run(test())