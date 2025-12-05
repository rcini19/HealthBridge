from datetime import date
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from donations.models import Donation
from requests.models import MedicineRequest
from notifications.models import Notification
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Clean up expired donations: delete from database, remove images from Supabase, and notify donors'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days-past-expiry',
            type=int,
            default=7,
            help='Delete donations expired for this many days (default: 7)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Delete all expired donations regardless of expiry date'
        )
    
    def handle(self, *args, **options):
        days_past = options['days_past_expiry']
        dry_run = options['dry_run']
        force = options['force']
        
        self.stdout.write("="*60)
        self.stdout.write(self.style.WARNING("EXPIRED DONATIONS CLEANUP"))
        self.stdout.write("="*60)
        
        try:
            deleted_count = self.cleanup_expired_donations(days_past, dry_run, force)
            
            if dry_run:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"\n✓ Dry run completed. Would have deleted {deleted_count} donations."
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"\n✓ Successfully cleaned up {deleted_count} expired donations!"
                    )
                )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n✗ Error: {str(e)}"))
            logger.exception("Cleanup command failed")
            raise
    
    @transaction.atomic
    def cleanup_expired_donations(self, days_past, dry_run, force):
        """Main cleanup logic"""
        
        # Get expired donations
        if force:
            expired_donations = Donation.objects.filter(expiry_date__lt=date.today())
            self.stdout.write(f"\nForce mode: Finding ALL expired donations...")
        else:
            from datetime import timedelta
            cutoff_date = date.today() - timedelta(days=days_past)
            expired_donations = Donation.objects.filter(expiry_date__lt=cutoff_date)
            self.stdout.write(f"\nFinding donations expired before {cutoff_date}...")
        
        total = expired_donations.count()
        self.stdout.write(f"Found {total} expired donation(s)\n")
        
        if total == 0:
            return 0
        
        deleted_count = 0
        
        for donation in expired_donations:
            days_expired = (date.today() - donation.expiry_date).days
            
            self.stdout.write("-" * 60)
            self.stdout.write(f"Medicine: {donation.name}")
            self.stdout.write(f"Tracking: {donation.tracking_code}")
            self.stdout.write(f"Expired: {donation.expiry_date} ({days_expired} days ago)")
            self.stdout.write(f"Donor: {donation.donor.email if donation.donor else 'Unknown'}")
            self.stdout.write(f"Image: {donation.image.name if donation.image else 'None'}")
            
            if dry_run:
                self.stdout.write(self.style.WARNING("[DRY RUN] Would delete this donation"))
                # Check for related requests
                related_requests = MedicineRequest.objects.filter(matched_donation=donation)
                if related_requests.exists():
                    self.stdout.write(self.style.WARNING(f"  [DRY RUN] Would also delete {related_requests.count()} related request(s)"))
                deleted_count += 1
            else:
                # 1. Handle related requests first (before deleting donation)
                related_requests = MedicineRequest.objects.filter(matched_donation=donation)
                if related_requests.exists():
                    try:
                        requests_deleted = self.delete_related_requests(donation, related_requests)
                        self.stdout.write(self.style.SUCCESS(f"  ✓ Deleted {requests_deleted} related request(s)"))
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"  ⚠ Request deletion failed: {e}"))
                
                # 2. Delete image from Supabase (if exists)
                if donation.image:
                    try:
                        self.delete_image_from_supabase(donation)
                        self.stdout.write(self.style.SUCCESS("  ✓ Image deleted from Supabase"))
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"  ⚠ Image deletion failed: {e}"))
                
                # 3. Create notification for donor (if exists)
                if donation.donor:
                    try:
                        self.notify_donor(donation, days_expired)
                        self.stdout.write(self.style.SUCCESS("  ✓ Donor notified"))
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"  ⚠ Notification failed: {e}"))
                
                # 4. Delete donation from database
                donation_name = donation.name
                donation.delete()
                self.stdout.write(self.style.SUCCESS(f"  ✓ Donation '{donation_name}' deleted from database"))
                deleted_count += 1
        
        return deleted_count
    
    def delete_related_requests(self, donation, related_requests):
        """Delete requests matched to this expired donation and notify recipients"""
        deleted_count = 0
        
        for request in related_requests:
            # Notify recipient before deleting
            try:
                self.notify_recipient(request, donation)
                logger.info(f"Notified recipient {request.recipient.email} about deleted request")
            except Exception as e:
                logger.error(f"Failed to notify recipient: {e}")
            
            # Delete the request
            request.delete()
            deleted_count += 1
        
        return deleted_count
    
    def notify_recipient(self, request, donation):
        """Create in-app notification for recipient about deleted request"""
        if not request.recipient:
            return
        
        try:
            notification = Notification.objects.create(
                user=request.recipient,
                notification_type=Notification.Type.SYSTEM,
                title=f"🗑️ Request Cancelled: Medicine Expired",
                message=(
                    f"Your request for '{request.medicine_name}' has been automatically cancelled "
                    f"because the matched medicine has expired and been removed from the system.\n\n"
                    f"Expired Medicine Details:\n"
                    f"• Medicine: {donation.name}\n"
                    f"• Tracking Code: {donation.tracking_code}\n"
                    f"• Expiry Date: {donation.expiry_date.strftime('%B %d, %Y')}\n\n"
                    f"Your Request Details:\n"
                    f"• Request Code: {request.tracking_code}\n"
                    f"• Quantity Requested: {request.quantity}\n"
                    f"• Urgency: {request.get_urgency_display()}\n\n"
                    f"We apologize for the inconvenience. Please submit a new request if you still need this medicine. "
                    f"Our team will help match you with available donations."
                ),
                request_id=request.id
            )
            logger.info(f"Created notification for recipient {request.recipient.email}")
            
        except Exception as e:
            logger.error(f"Failed to create recipient notification: {e}")
            raise
    
    def delete_image_from_supabase(self, donation):
        """Delete medicine image from Supabase storage"""
        if not donation.image:
            return
        
        try:
            # Import Supabase storage backend
            from HealthBridge.supabase_storage import SupabaseStorage
            import os
            
            storage = SupabaseStorage()
            file_path = donation.image.name
            
            # Delete from Supabase
            storage.delete(file_path)
            logger.info(f"Deleted image {file_path} from Supabase")
            
        except Exception as e:
            logger.error(f"Failed to delete image from Supabase: {e}")
            raise
    
    def notify_donor(self, donation, days_expired):
        """Create in-app notification for donor about deleted medicine"""
        if not donation.donor:
            return
        
        try:
            notification = Notification.objects.create(
                user=donation.donor,
                notification_type=Notification.Type.SYSTEM,
                title=f"🗑️ Expired Medicine Removed: {donation.name}",
                message=(
                    f"Your donated medicine '{donation.name}' has been automatically removed "
                    f"from the system as it expired {days_expired} days ago "
                    f"(expiry date: {donation.expiry_date.strftime('%B %d, %Y')}).\n\n"
                    f"Details:\n"
                    f"• Tracking Code: {donation.tracking_code}\n"
                    f"• Quantity: {donation.quantity}\n"
                    f"• Donated on: {donation.donated_at.strftime('%B %d, %Y')}\n\n"
                    f"Thank you for your contribution to HealthBridge! "
                    f"We encourage you to continue donating unexpired medicines to help those in need."
                ),
                donation_id=donation.id
            )
            logger.info(f"Created notification for user {donation.donor.email}")
            
        except Exception as e:
            logger.error(f"Failed to create notification: {e}")
            raise
    
    def get_urgency_color(self, days_expired):
        """Get color coding based on how long expired"""
        if days_expired > 30:
            return 'ERROR'  # Red - very old
        elif days_expired > 14:
            return 'WARNING'  # Yellow - moderately old
        else:
            return 'NOTICE'  # Blue - recently expired
