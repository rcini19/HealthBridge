import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HealthBridge.settings')
django.setup()

from requests.models import MedicineRequest
from donations.models import Donation
from django.utils import timezone
from datetime import timedelta

print("=" * 80)
print("PICKUP STATUS DIAGNOSTIC")
print("=" * 80)

# Get all claimed requests
claimed_requests = MedicineRequest.objects.filter(status='claimed').select_related('matched_donation', 'recipient')
print(f"\n📋 TOTAL CLAIMED REQUESTS: {claimed_requests.count()}")

for req in claimed_requests:
    print(f"\n{'='*60}")
    print(f"Request: {req.tracking_code}")
    print(f"  Medicine: {req.medicine_name}")
    print(f"  Recipient: {req.recipient.get_full_name()}")
    print(f"  Request Status: {req.status}")
    print(f"  Claimed Date: {req.updated_at}")
    print(f"  Has Matched Donation: {'Yes' if req.matched_donation else 'No'}")
    
    if req.matched_donation:
        donation = req.matched_donation
        print(f"\n  Matched Donation: {donation.tracking_code}")
        print(f"    Donation Name: {donation.name}")
        print(f"    Donor: {donation.donor.get_full_name() if donation.donor else 'Anonymous'}")
        print(f"    Donation Status: {donation.status}")
        print(f"    Last Updated: {donation.last_update}")
        
        # Check if qualifies for pickup
        if donation.status == 'delivered':
            print(f"  ✅ QUALIFIES FOR PICKUP (Request=claimed, Donation=delivered)")
        else:
            print(f"  ❌ DOES NOT QUALIFY - Donation status is '{donation.status}' (needs 'delivered')")
    else:
        print(f"  ❌ DOES NOT QUALIFY - No matched donation")

# Get all delivered donations
print(f"\n\n{'='*80}")
print("🚚 ALL DELIVERED DONATIONS")
print("=" * 80)

delivered_donations = Donation.objects.filter(status='delivered').select_related('donor')
print(f"Total delivered: {delivered_donations.count()}")

for donation in delivered_donations:
    print(f"\nDonation: {donation.tracking_code} - {donation.name}")
    print(f"  Donor: {donation.donor.get_full_name() if donation.donor else 'Anonymous'}")
    print(f"  Status: {donation.status}")
    print(f"  Last Updated: {donation.last_update}")
    
    # Find matched requests
    matched_reqs = MedicineRequest.objects.filter(matched_donation=donation)
    print(f"  Matched Requests: {matched_reqs.count()}")
    for req in matched_reqs:
        print(f"    - {req.tracking_code} (status: {req.status})")

# Final summary
print(f"\n\n{'='*80}")
print("SUMMARY")
print("=" * 80)

qualifying = MedicineRequest.objects.filter(
    status='claimed',
    matched_donation__isnull=False,
    matched_donation__status='delivered'
).count()

print(f"✅ Requests that QUALIFY for pickup section: {qualifying}")
print(f"   (Request status=claimed AND Donation status=delivered)")

print("\n" + "=" * 80)
