#!/usr/bin/env python3
"""Check if API key is loaded correctly."""
from app.core.config import get_settings

settings = get_settings()
key = settings.SENDGRID_API_KEY

print('API Key Configuration Check:')
print('-' * 60)
print(f'API Key loaded: {key}')
print(f'Starts with SG.: {key.startswith("SG.")}')
print(f'Length: {len(key)}')

# Check .env file
print('\n.env file content:')
with open('.env') as f:
    lines = f.readlines()
    for i, line in enumerate(lines, 1):
        if 'SENDGRID_API_KEY' in line and not line.startswith('#'):
            print(f'Line {i}: {line.strip()}')
