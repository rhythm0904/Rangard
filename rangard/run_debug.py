#!/usr/bin/env python3
"""Run the server with diagnostic output."""
import sys
sys.path.insert(0, '.')

print("1. Importing FastAPI app...")
from app.main import app
print("   ✅ App imported")

print("2. Starting server on http://127.0.0.1:8000...")
import uvicorn
uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
