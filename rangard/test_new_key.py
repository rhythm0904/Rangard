#!/usr/bin/env python3
"""Test SendGrid with new API key."""
from app.core.config import get_settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

settings = get_settings()
print('=' * 60)
print('Testing SendGrid with New API Key')
print('=' * 60)
print(f'\n1. Configuration loaded:')
print(f'   API Key: {settings.SENDGRID_API_KEY[:30]}...')
print(f'   From: {settings.EMAIL_FROM}')
print(f'   Name: {settings.EMAIL_FROM_NAME}')

try:
    print(f'\n2. Creating SendGrid client...')
    sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
    print('   ✅ Client created')
    
    print(f'\n3. Creating test message...')
    message = Mail(
        from_email=(settings.EMAIL_FROM, settings.EMAIL_FROM_NAME),
        to_emails='test@example.com',
        subject='RANGARD Test Email',
        html_content='<p>This is a test email from RANGARD</p>',
        plain_text_content='This is a test email from RANGARD',
    )
    print('   ✅ Message created')
    
    print(f'\n4. Sending email via SendGrid...')
    response = sg.send(message)
    
    print(f'   Response Status: {response.status_code}')
    
    if response.status_code in (200, 202):
        print('\n' + '=' * 60)
        print('✅ SUCCESS! EMAIL SENT!')
        print('=' * 60)
        print('\nThe new API key works correctly!')
        print('Email alerts are now ENABLED in the system.')
    else:
        print(f'\n❌ Unexpected status: {response.status_code}')
        print(f'Response: {response.body}')

except Exception as e:
    print(f'\n❌ Error: {e}')
    print(f'Error type: {type(e).__name__}')
    import traceback
    traceback.print_exc()
