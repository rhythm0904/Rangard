#!/usr/bin/env python3
"""Send threat alert to real email"""
import sys
sys.path.insert(0, '.')
from app.services.email import get_email_service

print("Sending threat alert...", flush=True)

email_svc = get_email_service()
success, error = email_svc.send_threat_alert(
    to_email='rhythmbhatnagar.cse22@jimsgn.org',
    to_name='Rhythm',
    filename='malware.exe',
    threat_level='high',
    confidence=0.9,
    patterns=['Encryption', 'File Lock'],
    scan_id='TEST-001'
)

if success:
    print("✅ Threat email sent!", flush=True)
else:
    print(f"❌ Error: {error}", flush=True)
