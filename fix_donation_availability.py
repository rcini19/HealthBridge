import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HealthBridge.settings')
django.setup()

from donations.models import Donation

print("=" * 80)
print("FIXING DONATION AVAILABILITY")
print("=" * 80)

# Find all donations marked as DELIVERED but still have quantity > 0
delivered_with_quantity = Donation.objects.filter(
    status='delivered',
    quantity__gt=0
)

print(f"\nFound {delivered_with_quantity.count()} delivered donations with remaining quantity")

fixed_count = 0
for donation in delivered_with_quantity:
    print(f"\n  Donation {donation.tracking_code} - {donation.name}")
    print(f"    Current status: {donation.status}")
    print(f"    Remaining quantity: {donation.quantity}")
    
    donation.status = Donation.Status.AVAILABLE
    donation.save()
    fixed_count += 1
    
    print(f"    ✅ Changed to: AVAILABLE (so others can request it)")

print(f"\n{'='*80}")
print(f"SUMMARY: Fixed {fixed_count} donations - they are now AVAILABLE for new requests")
print("=" * 80)

# Verify admin pickups still work (based on request CLAIMED status only)
from requests.models import MedicineRequest

claimed_requests = MedicineRequest.objects.filter(
    status='claimed',
    matched_donation__isnull=False
).count()

print(f"\n✅ Admin pickup count (requests that are CLAIMED): {claimed_requests}")
print("   (These will show in admin dashboard regardless of donation status)")
