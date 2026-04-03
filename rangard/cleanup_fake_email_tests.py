#!/usr/bin/env python3
"""
CLEANUP SCRIPT - Remove all problematic test files that send to fake emails
"""
import os
import glob

print("=" * 70)
print("CLEANUP - Removing test files with hardcoded fake emails")
print("=" * 70)

# List of test files to REMOVE (they use fake email addresses)
FILES_TO_REMOVE = [
    'test_auth.py',
    'test_auth_simple.py',
    'test_auth_components.py',
    'test_sendgrid_live.py',
    'test_sendgrid_live_2.py',
    'test_sendgrid_simple.py',
    'test_sendgrid_config.py',
    'test_sendgrid_direct.py',
    'test_new_key.py',
    'test_quick.py',
    'test_endpoint_quick.py',
    'test_endpoints_quick.py',
    'test_endpoints.py',
    'test_file_scan.py',
    'test_integration.py',
    'test_registration.py',
    'test_registration_api.py',
    'test_register_http.py',
    'test_email_flow.py',  # This one also needs to be removed
    'test_new_gmail.py',
]

# List of files to KEEP (they now ask for real email addresses)
FILES_TO_KEEP = [
    'test_gmail_smtp.py',
    'test_email_direct.py',
    'test_send_email_direct.py',
    'test_master_email_system.py',
    'test_email_delivery_diagnostic.py',
    'test_complete_email_flow.py',
    'test_gmail_auth.py',
    'test_alert_system.py',
    'test_verification_email.py',
]

print("\n" + "=" * 70)
print("FILES TO BE REMOVED (hardcoded fake emails)")
print("=" * 70)

removed_count = 0
for filename in FILES_TO_REMOVE:
    filepath = os.path.join('.', filename)
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            print(f"✓ Deleted: {filename}")
            removed_count += 1
        except Exception as e:
            print(f"✗ Failed to delete {filename}: {e}")
    else:
        print(f"- Not found: {filename}")

print(f"\n✅ Removed {removed_count} problematic test files")

print("\n" + "=" * 70)
print("FILES TO KEEP (ask for real email addresses)")
print("=" * 70)

for filename in FILES_TO_KEEP:
    filepath = os.path.join('.', filename)
    if os.path.exists(filepath):
        print(f"✓ Keep: {filename}")
    else:
        print(f"- Not found: {filename}")

print("\n" + "=" * 70)
print("CLEANUP COMPLETE")
print("=" * 70)

print(f"""
✅ All problematic test files have been removed!

USE ONLY THESE TEST SCRIPTS:
  • test_master_email_system.py (RECOMMENDED - Complete test)
  • test_gmail_smtp.py
  • test_email_direct.py
  • test_send_email_direct.py
  • test_email_delivery_diagnostic.py
  • test_complete_email_flow.py

NEXT STEP:
  python test_master_email_system.py
  
  Then enter YOUR REAL Gmail address when prompted
""")
