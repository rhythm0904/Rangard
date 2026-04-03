#!/usr/bin/env python3
"""Test SMTP connection."""
import smtplib
print("Testing SMTP connection...", flush=True)

try:
    print("Connecting to smtp.gmail.com:587...", flush=True)
    server = smtplib.SMTP("smtp.gmail.com", 587, timeout=5)
    print("✓ Connected!", flush=True)
    
    print("Starting TLS...", flush=True)
    server.starttls()
    print("✓ TLS started!", flush=True)
    
    server.quit()
    print("✓ Connection test successful!", flush=True)
except smtplib.SMTPException as e:
    print(f"❌ SMTP Error: {e}", flush=True)
except Exception as e:
    print(f"❌ Error: {e}", flush=True)
    import traceback
    traceback.print_exc()
