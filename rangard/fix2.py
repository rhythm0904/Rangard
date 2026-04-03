import asyncio
import sys
sys.path.insert(0, '.')

from app.core.database import engine
from sqlalchemy import text

async def fix():
    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS threat_intelligence"))
        await conn.execute(text("DROP TABLE IF EXISTS blockchain_records"))
        await conn.execute(text("DROP TABLE IF EXISTS quarantine_records"))
        await conn.execute(text("DROP TABLE IF EXISTS file_scans"))
        await conn.execute(text("DROP TABLE IF EXISTS users"))
        print("Dropped old tables")
    
    from app.core.database import create_tables
    await create_tables()
    print("Fresh tables created!")

asyncio.run(fix())