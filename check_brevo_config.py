"""
Quick check script to verify Brevo email configuration
"""
import os
import sys
import django
from pathlib import Path

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HealthBridge.settings')

# Suppress the loading message
os.environ['RUN_MAIN'] = 'true'
django.setup()

from django.conf import settings

print("=" * 60)
print("BREVO EMAIL CONFIGURATION CHECK")
print("=" * 60)

# Check environment variables
brevo_api_key = os.getenv('BREVO_API_KEY')
brevo_from_email = os.getenv('BREVO_FROM_EMAIL')
brevo_from_name = os.getenv('BREVO_FROM_NAME', 'HealthBridge')

print(f"\n{'Environment Variables:'}")
print(f"  BREVO_API_KEY: {'✅ SET (' + brevo_api_key[:20] + '...' + brevo_api_key[-10:] + ')' if brevo_api_key else '❌ NOT SET'}")
print(f"  BREVO_FROM_EMAIL: {brevo_from_email or '❌ NOT SET'}")
print(f"  BREVO_FROM_NAME: {brevo_from_name}")

print(f"\n{'Django Settings:'}")
print(f"  EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"  DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")

# Check if Brevo is active
is_brevo_active = 'brevo' in settings.EMAIL_BACKEND.lower()

print(f"\n{'Status:'}")
if is_brevo_active and brevo_api_key:
    print("  ✅ Brevo is ACTIVE and configured correctly!")
    print("  ✅ Your emails will be sent via Brevo API")
    print("  ✅ This will work on Render free tier!")
elif is_brevo_active:
    print("  ⚠️  Brevo backend is active but API key is missing")
    print("  ❌ Add BREVO_API_KEY to your .env file")
else:
    print(f"  ⚠️  Brevo backend is NOT active")
    print(f"  Current backend: {settings.EMAIL_BACKEND}")
    print(f"  Add BREVO_API_KEY to .env to activate Brevo")

print("=" * 60)

# Optional: Show SMTP backup config
smtp_login = os.getenv('BREVO_SMTP_LOGIN')
if smtp_login:
    print(f"\n{'SMTP Backup Configuration:'}")
    print(f"  BREVO_SMTP_SERVER: {os.getenv('BREVO_SMTP_SERVER', 'NOT SET')}")
    print(f"  BREVO_SMTP_LOGIN: {smtp_login}")
    print(f"  BREVO_SMTP_PORT: {os.getenv('BREVO_SMTP_PORT', 'NOT SET')}")
    print("=" * 60)
