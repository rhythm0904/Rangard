#!/usr/bin/env python
import sys
print(f"Python: {sys.version}")
print(f"Executable: {sys.executable}")
print(f"Path: {sys.path}")

sys.path.insert(0, '.')
print(f"Updated path: {sys.path[0]}")

try:
    print("\nImporting app modules...")
    from app.core.models import User, FileScan
    print("✓ Models imported")
    
    from app.core.database import AsyncSessionLocal
    print("✓ Database imported")
    
    from app.core.config import get_settings
    print("✓ Settings imported")
    
    settings = get_settings()
    print(f"✓ Settings loaded: DATABASE_URL={settings.DATABASE_URL}")
    
    # List tables
    import sqlite3
    conn = sqlite3.connect('rangard.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = cursor.fetchall()
    print(f"\n✓ Database has {len(tables)} tables: {[t[0] for t in tables]}")
    conn.close()
    
    print("\n✅ All imports successful!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
