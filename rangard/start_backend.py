#!/usr/bin/env python
"""
RANGARD Backend Startup Script
Simple, reliable server start without reload mode.
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, '.')
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("RANGARD BACKEND SERVER")
print("=" * 70)
print()

try:
    print("Loading application...")
    from app.main import app
    import uvicorn
    
    print("✓ Application loaded successfully")
    print()
    print("Starting server on http://127.0.0.1:8000")
    print("API documentation: http://127.0.0.1:8000/docs")
    print()
    print("Press CTRL+C to stop the server")
    print("=" * 70)
    print()
    
    # Start server without reload mode (simpler, more reliable)
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )
    
except KeyboardInterrupt:
    print("\n\nServer stopped.")
    sys.exit(0)
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
