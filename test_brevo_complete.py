"""
Test Brevo email configuration for HealthBridge
Tests both expiry notifications and password reset emails
"""
import os
import sys
import django
from pathlib import Path

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HealthBridge.settings')
django.setup()

from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def test_brevo_configuration():
    """Check if Brevo is properly configured"""
    print("\n" + "="*60)
    print("BREVO CONFIGURATION CHECK")
    print("="*60)
    
    # Check environment variables
    brevo_api_key = os.getenv('BREVO_API_KEY')
    brevo_from_email = os.getenv('BREVO_FROM_EMAIL')
    brevo_from_name = os.getenv('BREVO_FROM_NAME', 'HealthBridge')
    
    print(f"\n✓ BREVO_API_KEY: {'Set' if brevo_api_key else 'NOT SET'}")
    if brevo_api_key:
        print(f"  Key preview: {brevo_api_key[:20]}...{brevo_api_key[-10:]}")
    
    print(f"✓ BREVO_FROM_EMAIL: {brevo_from_email or 'NOT SET'}")
    print(f"✓ BREVO_FROM_NAME: {brevo_from_name}")
    print(f"\n✓ EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"✓ DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    
    # Check SMTP credentials (optional)
    smtp_key = os.getenv('BREVO_SMTP_KEY')
    smtp_server = os.getenv('BREVO_SMTP_SERVER')
    smtp_login = os.getenv('BREVO_SMTP_LOGIN')
    
    print(f"\n--- SMTP Credentials (Optional) ---")
    print(f"BREVO_SMTP_SERVER: {smtp_server or 'NOT SET'}")
    print(f"BREVO_SMTP_LOGIN: {smtp_login or 'NOT SET'}")
    print(f"BREVO_SMTP_KEY: {'Set' if smtp_key else 'NOT SET'}")
    
    if not brevo_api_key:
        print("\n❌ ERROR: BREVO_API_KEY is not set!")
        print("Please add it to your .env file:")
        print("BREVO_API_KEY=your_api_key_here")
        return False
    
    if not brevo_from_email:
        print("\n⚠ WARNING: BREVO_FROM_EMAIL is not set!")
        print("Using default from settings.py")
    
    return True


def test_simple_email(recipient_email):
    """Test sending a simple plain text email"""
    print("\n" + "="*60)
    print("TEST 1: SIMPLE PLAIN TEXT EMAIL")
    print("="*60)
    
    try:
        result = send_mail(
            subject='HealthBridge - Brevo Test Email',
            message='This is a test email from HealthBridge using Brevo API. If you receive this, Brevo is working correctly!',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            fail_silently=False,
        )
        
        if result == 1:
            print(f"\n✅ SUCCESS! Plain text email sent to {recipient_email}")
            print("Check your inbox (and spam folder)")
            return True
        else:
            print(f"\n❌ FAILED: Email not sent (result={result})")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR sending email: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_expiry_notification_email(recipient_email):
    """Test an expiry notification email (similar to your actual system)"""
    print("\n" + "="*60)
    print("TEST 2: MEDICINE EXPIRY NOTIFICATION EMAIL")
    print("="*60)
    
    # Sample data (simulating an expiring medicine)
    medicine_data = {
        'name': 'Paracetamol 500mg',
        'batch_number': 'BATCH-2024-001',
        'expiry_date': '2024-12-31',
        'quantity': '100 tablets',
        'days_until_expiry': 15,
    }
    
    subject = f"⚠️ Medicine Expiry Alert: {medicine_data['name']}"
    
    # Create HTML content
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
            .content {{ background-color: #f9f9f9; padding: 20px; border: 1px solid #ddd; }}
            .alert {{ background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
            .footer {{ text-align: center; padding: 20px; color: #777; font-size: 12px; }}
            .button {{ 
                display: inline-block; 
                padding: 10px 20px; 
                background-color: #4CAF50; 
                color: white !important; 
                text-decoration: none; 
                border-radius: 5px; 
                margin: 10px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏥 HealthBridge</h1>
                <p>Medicine Inventory System</p>
            </div>
            
            <div class="content">
                <h2>Medicine Expiry Alert</h2>
                
                <div class="alert">
                    <strong>⚠️ Attention Required!</strong>
                    <p>The following medicine is approaching its expiration date:</p>
                </div>
                
                <h3>Medicine Details:</h3>
                <ul>
                    <li><strong>Name:</strong> {medicine_data['name']}</li>
                    <li><strong>Batch Number:</strong> {medicine_data['batch_number']}</li>
                    <li><strong>Expiry Date:</strong> {medicine_data['expiry_date']}</li>
                    <li><strong>Quantity:</strong> {medicine_data['quantity']}</li>
                    <li><strong>Days Until Expiry:</strong> <span style="color: red; font-weight: bold;">{medicine_data['days_until_expiry']} days</span></li>
                </ul>
                
                <p><strong>Action Required:</strong> Please review this medicine and take appropriate action before it expires.</p>
                
                <a href="#" class="button">View in Dashboard</a>
            </div>
            
            <div class="footer">
                <p>This is an automated email from HealthBridge Medicine Inventory System</p>
                <p>© 2024 HealthBridge. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Create plain text version
    text_content = f"""
    HEALTHBRIDGE - MEDICINE EXPIRY ALERT
    
    ⚠️ Attention Required!
    
    The following medicine is approaching its expiration date:
    
    Medicine Details:
    - Name: {medicine_data['name']}
    - Batch Number: {medicine_data['batch_number']}
    - Expiry Date: {medicine_data['expiry_date']}
    - Quantity: {medicine_data['quantity']}
    - Days Until Expiry: {medicine_data['days_until_expiry']} days
    
    Action Required: Please review this medicine and take appropriate action before it expires.
    
    ---
    This is an automated email from HealthBridge Medicine Inventory System
    © 2024 HealthBridge. All rights reserved.
    """
    
    try:
        # Create multipart email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email]
        )
        email.attach_alternative(html_content, "text/html")
        
        result = email.send(fail_silently=False)
        
        if result == 1:
            print(f"\n✅ SUCCESS! Expiry notification email sent to {recipient_email}")
            print("Check your inbox for a formatted HTML email with medicine details")
            return True
        else:
            print(f"\n❌ FAILED: Email not sent (result={result})")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR sending email: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_password_reset_email(recipient_email):
    """Test a password reset email"""
    print("\n" + "="*60)
    print("TEST 3: PASSWORD RESET EMAIL")
    print("="*60)
    
    # Generate a fake reset token
    reset_token = "test-reset-token-123456789"
    reset_url = f"http://localhost:8000/reset-password/{reset_token}/"
    
    subject = "HealthBridge - Password Reset Request"
    
    # Create HTML content
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #2196F3; color: white; padding: 20px; text-align: center; }}
            .content {{ background-color: #f9f9f9; padding: 20px; border: 1px solid #ddd; }}
            .button {{ 
                display: inline-block; 
                padding: 12px 30px; 
                background-color: #2196F3; 
                color: white !important; 
                text-decoration: none; 
                border-radius: 5px; 
                margin: 20px 0;
                font-weight: bold;
            }}
            .footer {{ text-align: center; padding: 20px; color: #777; font-size: 12px; }}
            .warning {{ background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏥 HealthBridge</h1>
                <p>Password Reset Request</p>
            </div>
            
            <div class="content">
                <h2>Reset Your Password</h2>
                
                <p>Hello,</p>
                
                <p>We received a request to reset your password for your HealthBridge account.</p>
                
                <p>Click the button below to reset your password:</p>
                
                <div style="text-align: center;">
                    <a href="{reset_url}" class="button">Reset Password</a>
                </div>
                
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; background-color: #eee; padding: 10px; font-family: monospace;">
                    {reset_url}
                </p>
                
                <div class="warning">
                    <strong>⚠️ Security Note:</strong>
                    <ul>
                        <li>This link will expire in 24 hours</li>
                        <li>If you didn't request this, please ignore this email</li>
                        <li>Never share this link with anyone</li>
                    </ul>
                </div>
            </div>
            
            <div class="footer">
                <p>This is an automated email from HealthBridge</p>
                <p>© 2024 HealthBridge. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Create plain text version
    text_content = f"""
    HEALTHBRIDGE - PASSWORD RESET REQUEST
    
    Hello,
    
    We received a request to reset your password for your HealthBridge account.
    
    Click the link below to reset your password:
    {reset_url}
    
    Security Note:
    - This link will expire in 24 hours
    - If you didn't request this, please ignore this email
    - Never share this link with anyone
    
    ---
    This is an automated email from HealthBridge
    © 2024 HealthBridge. All rights reserved.
    """
    
    try:
        # Create multipart email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email]
        )
        email.attach_alternative(html_content, "text/html")
        
        result = email.send(fail_silently=False)
        
        if result == 1:
            print(f"\n✅ SUCCESS! Password reset email sent to {recipient_email}")
            print("Check your inbox for a formatted password reset email")
            return True
        else:
            print(f"\n❌ FAILED: Email not sent (result={result})")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR sending email: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    print("\n" + "="*60)
    print("HEALTHBRIDGE BREVO EMAIL TEST SUITE")
    print("="*60)
    
    # Check configuration first
    if not test_brevo_configuration():
        print("\n❌ Configuration check failed. Please fix the issues above and try again.")
        return
    
    # Get recipient email
    recipient = input("\nEnter your email address to receive test emails: ").strip()
    if not recipient:
        print("❌ No email provided. Exiting.")
        return
    
    print(f"\n📧 Test emails will be sent to: {recipient}")
    print("\nStarting tests...\n")
    
    # Run all tests
    results = {
        'simple': test_simple_email(recipient),
        'expiry': test_expiry_notification_email(recipient),
        'password_reset': test_password_reset_email(recipient),
    }
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"\n{'Test':<30} {'Result':<10}")
    print("-" * 60)
    print(f"{'Simple Email':<30} {'✅ PASS' if results['simple'] else '❌ FAIL'}")
    print(f"{'Expiry Notification':<30} {'✅ PASS' if results['expiry'] else '❌ FAIL'}")
    print(f"{'Password Reset':<30} {'✅ PASS' if results['password_reset'] else '❌ FAIL'}")
    print("-" * 60)
    
    passed = sum(results.values())
    total = len(results)
    print(f"\nTests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED! Brevo is configured correctly.")
        print("Your expiry notifications and password reset emails will work on Render!")
    else:
        print("\n⚠️ Some tests failed. Please check the error messages above.")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
