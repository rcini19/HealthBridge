"""
Quick test for password reset email functionality
Tests the actual Django password reset flow
"""
import os
import sys
import django
from pathlib import Path

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HealthBridge.settings')
os.environ['RUN_MAIN'] = 'true'  # Suppress duplicate loading messages
django.setup()

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

User = get_user_model()

print("\n" + "="*60)
print("PASSWORD RESET EMAIL TEST")
print("="*60)

# Check email backend
print(f"\nEmail Backend: {settings.EMAIL_BACKEND}")
print(f"From Email: {settings.DEFAULT_FROM_EMAIL}")

brevo_key = os.getenv('BREVO_API_KEY')
if brevo_key:
    print(f"✓ Brevo API Key: {brevo_key[:20]}...{brevo_key[-10:]}")
else:
    print("⚠ Brevo API Key: NOT SET")

print("\n" + "-"*60)

# Get test user email
test_email = input("\nEnter a user email address from your database: ").strip()

if not test_email:
    print("❌ No email provided. Exiting.")
    sys.exit(1)

# Check if user exists
try:
    user = User.objects.get(email=test_email)
    print(f"✓ Found user: {user.email}")
except User.DoesNotExist:
    print(f"❌ User with email '{test_email}' not found in database!")
    print("\nCreate a user first or use an existing email.")
    sys.exit(1)

print("\n" + "-"*60)
print("SENDING PASSWORD RESET EMAIL...")
print("-"*60)

# Generate reset token
token = default_token_generator.make_token(user)
uid = urlsafe_base64_encode(force_bytes(user.pk))

# Create reset URL
reset_url = f"http://localhost:8000/login/password-reset-confirm/{uid}/{token}/"

# Email subject and message
subject = "HealthBridge - Password Reset Request"

html_message = f"""
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
        }}
        .footer {{ text-align: center; padding: 20px; color: #777; font-size: 12px; }}
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
            <p>Hello {user.first_name or user.email},</p>
            <p>We received a request to reset your password.</p>
            <p>Click the button below to reset your password:</p>
            
            <div style="text-align: center;">
                <a href="{reset_url}" class="button">Reset Password</a>
            </div>
            
            <p>Or copy this link: {reset_url}</p>
            <p style="color: #999; font-size: 12px;">This link expires in 24 hours.</p>
        </div>
        
        <div class="footer">
            <p>This is an automated email from HealthBridge</p>
        </div>
    </div>
</body>
</html>
"""

text_message = f"""
HealthBridge - Password Reset Request

Hello {user.first_name or user.email},

We received a request to reset your password.

Click this link to reset your password:
{reset_url}

This link expires in 24 hours.

If you didn't request this, please ignore this email.

---
This is an automated email from HealthBridge
"""

try:
    # Import EmailMultiAlternatives for HTML email
    from django.core.mail import EmailMultiAlternatives
    
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[test_email]
    )
    email.attach_alternative(html_message, "text/html")
    
    result = email.send(fail_silently=False)
    
    if result == 1:
        print("\n✅ SUCCESS! Password reset email sent!")
        print(f"   To: {test_email}")
        print(f"   Via: {settings.EMAIL_BACKEND}")
        print("\n📧 Check your inbox (and spam folder)")
        print("\n🔗 Reset URL:")
        print(f"   {reset_url}")
        print("\n" + "="*60)
    else:
        print(f"\n❌ FAILED: Email not sent (result={result})")
        print("="*60)
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    print("\n" + "="*60)
