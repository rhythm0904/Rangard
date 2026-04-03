#!/bin/bash

# Install backend dependencies
cd rangard
echo "📦 Installing Python dependencies..."
pip install  -r requirements.txt

# Create database tables (optional - will run on first startup if needed)
echo "🔧 Attempting database setup..."
python -c "
import asyncio
import sys
from app.core.database import create_tables
try:
    asyncio.run(create_tables())
    print('✓ Database tables created/verified')
except Exception as e:
    print(f'⚠ Database setup skipped (will run on first startup): {e}')
    # Don't exit with error - database will be initialized on first run
    sys.exit(0)
" || true

echo "✅ Build completed successfully"
