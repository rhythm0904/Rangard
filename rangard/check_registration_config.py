#!/usr/bin/env python
"""Quick diagnostic to identify registration issues."""
import sys
sys.path.insert(0, '.')

print("REGISTRATION DIAGNOSTIC")
print("=" * 60)

try:
    print("\n1. Testing imports...")
    from app.core.config import get_settings
    from app.services.email import get_email_service
    print("   ✓ Imports successful")
    
    print("\n2. Checking configuration...")
    settings = get_settings()
    print(f"   APP_ENV: {settings.APP_ENV}")
    print(f"   FRONTEND_URL: {settings.FRONTEND_URL}")
    print(f"   DATABASE_URL: {settings.DATABASE_URL}")
    
    print("\n3. Checking email service...")
    email_svc = get_email_service()
    print(f"   Email service initialized: OK")
    print(f"   Gmail user: {email_svc.gmail_user if email_svc.gmail_user else 'NOT SET'}")
    print(f"   Gmail password: {'SET' if email_svc.gmail_password else 'NOT SET'}")
    print(f"   SMTP server: {email_svc.smtp_server}:{email_svc.smtp_port}")
    
    if not email_svc.gmail_user or not email_svc.gmail_password:
        print("\n   ⚠️  EMAIL NOT CONFIGURED!")
        print("   Check .env file for GMAIL_APP_PASSWORD")
        sys.exit(1)
    
    print("\n✅ Configuration looks good!")
    print("   Issue must be in the frontend or specific error.")
    print("   Check browser console for detailed error message.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
