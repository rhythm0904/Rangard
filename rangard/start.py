#!/usr/bin/env python
"""
Simple backend startup - shows all errors clearly.
"""
import sys
import os

sys.path.insert(0, '.')
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("Starting RANGARD Backend Server...")
print()

try:
    from app.main import app
    import uvicorn
    
    # Run directly
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
