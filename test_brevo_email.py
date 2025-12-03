"""
Test script for Brevo email backend
Run this to verify your Brevo configuration is working correctly.
"""

import os
import sys
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HealthBridge.settings')
import django
django.setup()

from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings


def test_simple_email():
    """Test sending a simple plain text email"""
    print("\n" + "="*60)
    print("TEST 1: Sending Simple Plain Text Email")
    print("="*60)
    
    try:
        result = send_mail(
            subject='HealthBridge - Test Email (Plain Text)',
            message='This is a plain text test email sent via Brevo API.\n\nIf you receive this, your Brevo configuration is working correctly!',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[input("Enter your email address to receive test: ")],
            fail_silently=False,
        )
        
        if result:
            print("✅ SUCCESS: Plain text email sent successfully!")
            print(f"   - Sent to: {result} recipient(s)")
            print(f"   - From: {settings.DEFAULT_FROM_EMAIL}")
        else:
            print("❌ FAILED: Email was not sent")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


def test_html_email():
    """Test sending an HTML email"""
    print("\n" + "="*60)
    print("TEST 2: Sending HTML Email")
    print("="*60)
    
    try:
        recipient = input("Enter your email address to receive HTML test: ")
        
        # Create the email
        subject = 'HealthBridge - Test Email (HTML)'
        text_content = 'This is the plain text version of the email.'
        html_content = '''
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: #4CAF50; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background: #f5f5f5; }
                .footer { text-align: center; padding: 10px; font-size: 12px; color: #666; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏥 HealthBridge</h1>
                </div>
                <div class="content">
                    <h2>Test Email - HTML Format</h2>
                    <p>Hello!</p>
                    <p>This is a <strong>test HTML email</strong> sent via <em>Brevo API</em>.</p>
                    <p>If you're seeing this beautifully formatted message, your Brevo configuration is working perfectly!</p>
                    <ul>
                        <li>✅ Brevo API configured correctly</li>
                        <li>✅ HTML emails working</li>
                        <li>✅ Ready for production</li>
                    </ul>
                </div>
                <div class="footer">
                    <p>Sent from HealthBridge via Brevo</p>
                </div>
            </div>
        </body>
        </html>
        '''
        
        msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [recipient])
        msg.attach_alternative(html_content, "text/html")
        result = msg.send(fail_silently=False)
        
        if result:
            print("✅ SUCCESS: HTML email sent successfully!")
            print(f"   - Sent to: {recipient}")
            print(f"   - From: {settings.DEFAULT_FROM_EMAIL}")
        else:
            print("❌ FAILED: Email was not sent")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


def check_configuration():
    """Check if Brevo is properly configured"""
    print("\n" + "="*60)
    print("BREVO CONFIGURATION CHECK")
    print("="*60)
    
    print(f"\nEmail Backend: {settings.EMAIL_BACKEND}")
    print(f"Default From Email: {settings.DEFAULT_FROM_EMAIL}")
    
    brevo_key = os.getenv('BREVO_API_KEY')
    if brevo_key:
        print(f"✅ Brevo API Key: {'*' * 20}{brevo_key[-4:]}")
    else:
        print("❌ Brevo API Key: NOT CONFIGURED")
        print("\n⚠️  WARNING: BREVO_API_KEY not found in environment variables!")
        print("   Please add it to your .env file:")
        print("   BREVO_API_KEY=your_api_key_here")
        print("   BREVO_FROM_EMAIL=your_verified_email@domain.com")
        return False
    
    return True


def main():
    """Main test function"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           BREVO EMAIL BACKEND TEST SCRIPT                    ║
║                                                              ║
║  This script will test your Brevo email configuration       ║
║  and send test emails to verify everything is working.      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Check configuration first
    if not check_configuration():
        print("\n❌ Configuration check failed. Please fix the issues above.")
        return
    
    print("\n✅ Configuration looks good!")
    print("\nWe'll now send test emails to verify the setup.")
    
    # Ask user what tests to run
    print("\nSelect tests to run:")
    print("1. Plain text email only")
    print("2. HTML email only")
    print("3. Both tests")
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice in ['1', '3']:
        test_simple_email()
    
    if choice in ['2', '3']:
        test_html_email()
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
    print("\nCheck your email inbox (and spam folder) for the test emails.")
    print("Also check your Brevo dashboard at https://app.brevo.com/")
    print("for email statistics and delivery confirmation.")
    print("\n")


if __name__ == '__main__':
    main()
