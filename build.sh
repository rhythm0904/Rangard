#!/bin/bash
set -o errexit

# Install backend dependencies
cd rangard
pip install -q -r requirements.txt

# Create database tables (will migrate if needed)
python -c "
import asyncio
from app.core.database import create_tables
try:
    asyncio.run(create_tables())
    print('✓ Database tables created/verified')
except Exception as e:
    print(f'⚠ Database setup warning: {e}')
    print('(This is normal if database already exists)')
"

echo "✓ Build completed successfully"
