#!/usr/bin/env python
"""Quick test of verify-email endpoint"""
import requests
import json

BASE_URL = "http://localhost:8000"

# Test with invalid token to see if endpoint exists
data = {"token": "test_token"}
response = requests.post(f"{BASE_URL}/api/auth/verify-email", json=data)

print(f"Endpoint: POST /api/auth/verify-email")
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 404:
    print("\n❌ Endpoint NOT FOUND")
    print("Checking available endpoints...")
    
    # List all endpoints
    docs_response = requests.get(f"{BASE_URL}/openapi.json")
    if docs_response.status_code == 200:
        openapi = docs_response.json()
        paths = openapi.get("paths", {})
        print("\nAvailable paths:")
        for path in sorted(paths.keys()):
            methods = list(paths[path].keys())
            print(f"  {methods} {path}")
else:
    print("\n✅ Endpoint EXISTS!")
