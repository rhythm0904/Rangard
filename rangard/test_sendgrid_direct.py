#!/usr/bin/env python3
"""Test SendGrid API directly to verify it's working."""
import sys
sys.path.insert(0, '.')

from app.core.config import get_settings

settings = get_settings()

print("=" * 60)
print("SendGrid Direct API Test")  
print("=" * 60)

print("\n1. Configuration Check")
print(f"   SENDGRID_API_KEY: {settings.SENDGRID_API_KEY[:20]}...")
print(f"   EMAIL_FROM: {settings.EMAIL_FROM}")
print(f"   EMAIL_FROM_NAME: {settings.EMAIL_FROM_NAME}")
print(f"   APP_ENV: {settings.APP_ENV}")

print("\n2. Testing Direct SendGrid API Call")
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    
    sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
    print("   ✅ SendGridAPIClient created")
    
    # Create a test message
    message = Mail(
        from_email=(settings.EMAIL_FROM, settings.EMAIL_FROM_NAME),
        to_emails="test@example.com",
        subject="RANGARD Test Email",
        html_content="<p>This is a test email from RANGARD</p>",
        plain_text_content="This is a test email from RANGARD",
    )
    print("   ✅ Message object created")
    
    # Send the message
    print("\n3. Attempting to send email...")
    response = sg.send(message)
    print(f"   Response Status Code: {response.status_code}")
    print(f"   Response Headers: {dict(response.headers)}")
    print(f"   Response Body: {response.body if hasattr(response, 'body') else 'N/A'}")
    
    if response.status_code in (200, 202):
        print("   ✅ EMAIL SENT SUCCESSFULLY!")
    else:
        print(f"   ❌ Unexpected status code: {response.status_code}")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    print(f"   Error type: {type(e).__name__}")
    print(f"   Error details:")
    
    if hasattr(e, 'http_status_code'):
        print(f"      HTTP Status: {e.http_status_code}")
    if hasattr(e, 'error'):
        print(f"      Error message: {e.error}")
    if hasattr(e, 'body'):
        print(f"      Body: {e.body}")
        
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
