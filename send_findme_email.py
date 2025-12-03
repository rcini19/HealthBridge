"""
Send a test email with a very distinctive subject to help locate it
"""
import os
import sys
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HealthBridge.settings')
os.environ['RUN_MAIN'] = 'true'
django.setup()

from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import time

print("\n" + "="*60)
print("🔔 SENDING DISTINCTIVE TEST EMAIL")
print("="*60)

recipient = input("\nEnter your email address: ").strip()
if not recipient:
    print("No email provided!")
    sys.exit(1)

# Create a very distinctive subject
subject = "🚨 TEST EMAIL 12345 - FIND ME IN YOUR INBOX! 🚨"

html_content = """
<html>
<head>
    <style>
        body { font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px; }
        .container { background: white; padding: 40px; border-radius: 10px; max-width: 600px; margin: 0 auto; box-shadow: 0 10px 40px rgba(0,0,0,0.3); }
        h1 { color: #667eea; font-size: 32px; text-align: center; }
        .alert { background: #ffd700; border: 3px solid #ff6b6b; padding: 20px; margin: 20px 0; border-radius: 5px; text-align: center; font-size: 24px; font-weight: bold; color: #333; }
        .success { background: #4CAF50; color: white; padding: 20px; border-radius: 5px; text-align: center; margin: 20px 0; }
        .info { background: #e3f2fd; padding: 15px; border-left: 4px solid #2196F3; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎉 SUCCESS! EMAIL IS WORKING! 🎉</h1>
        
        <div class="alert">
            ⚠️ YOU FOUND THE EMAIL! ⚠️
        </div>
        
        <div class="success">
            <h2>✅ Brevo Email System is WORKING!</h2>
            <p>If you're reading this, emails are being delivered successfully!</p>
        </div>
        
        <div class="info">
            <h3>📧 Email Details:</h3>
            <ul>
                <li><strong>Sent via:</strong> Brevo API</li>
                <li><strong>From:</strong> HealthBridge</li>
                <li><strong>To:</strong> """ + recipient + """</li>
                <li><strong>Status:</strong> DELIVERED ✅</li>
            </ul>
        </div>
        
        <div class="info">
            <h3>🔍 Where was this email?</h3>
            <p>Check which folder you found this in:</p>
            <ul>
                <li>📥 Primary Inbox</li>
                <li>📢 Promotions Tab</li>
                <li>🗑️ Spam/Junk Folder</li>
            </ul>
            <p><strong>Mark as "Not Spam"</strong> if found in spam to ensure future emails go to inbox!</p>
        </div>
        
        <div class="success">
            <p style="font-size: 18px; margin: 0;">
                <strong>Your HealthBridge system is ready for production!</strong>
            </p>
            <p style="margin: 10px 0 0 0;">
                Password resets and expiry notifications will work perfectly! 🚀
            </p>
        </div>
        
        <p style="text-align: center; color: #999; margin-top: 30px; font-size: 12px;">
            Test email sent on December 3, 2025<br>
            HealthBridge Medicine Inventory System
        </p>
    </div>
</body>
</html>
"""

text_content = f"""
🚨 TEST EMAIL - FIND ME IN YOUR INBOX! 🚨

SUCCESS! EMAIL IS WORKING!

If you're reading this, emails are being delivered successfully!

Email Details:
- Sent via: Brevo API
- From: HealthBridge  
- To: {recipient}
- Status: DELIVERED ✅

Where was this email?
Check which folder you found this in:
- Primary Inbox
- Promotions Tab  
- Spam/Junk Folder

Mark as "Not Spam" if found in spam!

Your HealthBridge system is ready for production!
Password resets and expiry notifications will work perfectly!

---
Test email sent on December 3, 2025
HealthBridge Medicine Inventory System
"""

print(f"\n📧 Sending to: {recipient}")
print(f"📝 Subject: {subject}")
print(f"🚀 Via: {settings.EMAIL_BACKEND}")
print("\nSending...")

try:
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient]
    )
    email.attach_alternative(html_content, "text/html")
    
    result = email.send(fail_silently=False)
    
    if result == 1:
        print("\n" + "="*60)
        print("✅ EMAIL SENT SUCCESSFULLY!")
        print("="*60)
        print("\n🔍 NOW CHECK YOUR EMAIL:")
        print("\n   1. Open Gmail")
        print("   2. Search for: '12345' or 'FIND ME'")
        print("   3. Check ALL folders (Primary, Promotions, Spam)")
        print("\n⏰ Email should arrive in 10-60 seconds")
        print("\n📱 Refresh your inbox and check!")
        print("\n" + "="*60)
        
        # Countdown
        print("\n⏰ Waiting 60 seconds for email to arrive...")
        print("   Check your email NOW!")
        for i in range(60, 0, -10):
            print(f"   {i} seconds... (keep checking your email)")
            time.sleep(10)
        
        print("\n✅ Email should have arrived by now!")
        print("   If not in Primary, check Spam/Promotions folders!")
        print("\n" + "="*60 + "\n")
    else:
        print(f"\n❌ Failed to send (result={result})")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
