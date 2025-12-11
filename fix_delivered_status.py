import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HealthBridge.settings')
django.setup()

from requests.models import MedicineRequest
from donations.models import Donation

print("=" * 80)
print("FIXING EXISTING DELIVERED DONATIONS")
print("=" * 80)

# Find all requests that are FULFILLED or CLAIMED with matched donations
fulfilled_or_claimed = MedicineRequest.objects.filter(
    status__in=['fulfilled', 'claimed'],
    matched_donation__isnull=False
).select_related('matched_donation')

print(f"\nFound {fulfilled_or_claimed.count()} fulfilled/claimed requests with matched donations")

fixed_count = 0
for req in fulfilled_or_claimed:
    donation = req.matched_donation
    
    # If donation status is not already DELIVERED, fix it
    if donation.status != 'delivered':
        print(f"\n  Fixing donation {donation.tracking_code}")
        print(f"    Old status: {donation.status}")
        print(f"    Request {req.tracking_code} is {req.status}")
        
        donation.status = Donation.Status.DELIVERED
        donation.save()
        fixed_count += 1
        
        print(f"    ✅ Updated to: delivered")

print(f"\n{'='*80}")
print(f"SUMMARY: Fixed {fixed_count} donations")
print("=" * 80)
