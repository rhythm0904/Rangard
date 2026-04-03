import asyncio
import sys
sys.path.insert(0, '.')
from app.core.database import create_tables
asyncio.run(create_tables())
print('Tables created successfully!')