"""
Debug Brevo sender verification and email delivery
"""
import os
import sys
import django
from pathlib import Path

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HealthBridge.settings')
os.environ['RUN_MAIN'] = 'true'
django.setup()

import httpx

print("\n" + "="*60)
print("BREVO ACCOUNT & SENDER VERIFICATION CHECK")
print("="*60)

api_key = os.getenv('BREVO_API_KEY')
from_email = os.getenv('BREVO_FROM_EMAIL', 'healthbridge.expiryalerts123@gmail.com')

if not api_key:
    print("❌ BREVO_API_KEY not found!")
    sys.exit(1)

print(f"\n✓ API Key: {api_key[:20]}...{api_key[-10:]}")
print(f"✓ From Email: {from_email}")

# Check Brevo account info
print("\n" + "-"*60)
print("CHECKING BREVO ACCOUNT...")
print("-"*60)

headers = {
    "accept": "application/json",
    "api-key": api_key
}

try:
    # Get account info
    with httpx.Client(timeout=10.0) as client:
        response = client.get(
            "https://api.brevo.com/v3/account",
            headers=headers
        )
        
        if response.status_code == 200:
            account = response.json()
            print(f"\n✓ Account Email: {account.get('email', 'N/A')}")
            print(f"✓ Company Name: {account.get('companyName', 'N/A')}")
            
            # Get plan info
            plan = account.get('plan', [{}])
            if plan:
                plan_info = plan[0] if isinstance(plan, list) else plan
                print(f"✓ Plan Type: {plan_info.get('type', 'N/A')}")
                credits = plan_info.get('credits', {})
                print(f"✓ Email Credits Remaining: {credits.get('emailCredits', 'N/A')}")
        else:
            print(f"⚠ Could not get account info: {response.status_code}")
            
except Exception as e:
    print(f"⚠ Error checking account: {e}")

# Check senders
print("\n" + "-"*60)
print("CHECKING VERIFIED SENDERS...")
print("-"*60)

try:
    with httpx.Client(timeout=10.0) as client:
        response = client.get(
            "https://api.brevo.com/v3/senders",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            senders = data.get('senders', [])
            
            if not senders:
                print("\n⚠️  NO SENDERS CONFIGURED!")
                print("\n🔴 THIS IS THE PROBLEM!")
                print("\nYou need to add and verify a sender in Brevo:")
                print("1. Go to: https://app.brevo.com/senders")
                print("2. Click 'Add a sender'")
                print(f"3. Add email: {from_email}")
                print("4. Verify the email (check inbox for verification link)")
                print("\nUntil verified, emails will be BLOCKED by Brevo!")
            else:
                print(f"\n✓ Found {len(senders)} sender(s):")
                for sender in senders:
                    email = sender.get('email', 'N/A')
                    name = sender.get('name', 'N/A')
                    active = sender.get('active', False)
                    
                    status = "✅ ACTIVE" if active else "❌ INACTIVE"
                    print(f"\n  Email: {email}")
                    print(f"  Name: {name}")
                    print(f"  Status: {status}")
                    
                    if email == from_email:
                        if active:
                            print(f"  🎉 Your sender email is VERIFIED!")
                        else:
                            print(f"  🔴 Your sender email is NOT ACTIVE!")
                            print(f"     Go to https://app.brevo.com/senders to verify it")
                    
                # Check if our from_email is in the list
                sender_emails = [s.get('email') for s in senders]
                if from_email not in sender_emails:
                    print(f"\n⚠️  WARNING: {from_email} is NOT in verified senders!")
                    print(f"   Add it at: https://app.brevo.com/senders")
        else:
            print(f"⚠ Could not get senders: {response.status_code}")
            print(f"   Response: {response.text}")
            
except Exception as e:
    print(f"⚠ Error checking senders: {e}")

# Check recent email activity
print("\n" + "-"*60)
print("CHECKING RECENT EMAIL ACTIVITY...")
print("-"*60)

try:
    with httpx.Client(timeout=10.0) as client:
        # Get email events from last hour
        import urllib.parse
        from datetime import datetime, timedelta
        
        # Get events from last 24 hours
        response = client.get(
            "https://api.brevo.com/v3/smtp/statistics/events",
            headers=headers,
            params={
                "limit": 10,
                "offset": 0,
                "days": 1
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            events = data.get('events', [])
            
            if events:
                print(f"\n✓ Found {len(events)} recent email events:")
                for event in events[:5]:  # Show last 5
                    print(f"\n  Email: {event.get('email', 'N/A')}")
                    print(f"  Event: {event.get('event', 'N/A')}")
                    print(f"  Date: {event.get('date', 'N/A')}")
                    print(f"  Subject: {event.get('subject', 'N/A')}")
            else:
                print("\n⚠ No recent email events found")
                print("   This might mean emails aren't being sent yet")
        else:
            print(f"⚠ Could not get email events: {response.status_code}")
            
except Exception as e:
    print(f"⚠ Error checking email events: {e}")

print("\n" + "="*60)
print("RECOMMENDATIONS")
print("="*60)

print("\n1. 🔍 CHECK SPAM FOLDER in your email")
print("2. ⏰ WAIT 2-5 minutes for email to arrive")
print("3. 👤 VERIFY SENDER at https://app.brevo.com/senders")
print("4. 📊 CHECK DASHBOARD at https://app.brevo.com/statistics/email")
print("5. 📝 CHECK LOGS at https://app.brevo.com/logs")

print("\n" + "="*60)
print("\n💡 TIP: The email was sent to Brevo successfully.")
print("   If it's not arriving, the issue is likely:")
print("   - Sender not verified in Brevo")
print("   - Email going to spam")
print("   - Brevo account limitations")
print("\n" + "="*60 + "\n")
