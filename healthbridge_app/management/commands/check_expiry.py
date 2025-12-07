from datetime import date, timedelta
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail, send_mass_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from donations.models import Donation, ExpiryAlert


class Command(BaseCommand):
    help = 'Check for medicines expiring within specified days and send notifications'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=10,
            help='Number of days before expiry to send alerts (default: 10)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without sending emails'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Send alerts even if already sent (ignore duplicates)'
        )
        parser.add_argument(
            '--critical-only',
            action='store_true',
            help='Only send alerts for medicines expiring in 3 days or less'
        )
    
    def handle(self, *args, **options):
        days_ahead = options['days']
        dry_run = options['dry_run']
        force = options['force']
        critical_only = options['critical_only']
        
        if critical_only:
            days_ahead = min(days_ahead, 3)
            self.stdout.write(f"Critical mode: checking medicines expiring within {days_ahead} days")
        
        try:
            notifications_sent = self.process_expiry_notifications(
                days_ahead, dry_run, force
            )
            
            if dry_run:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Dry run completed. Would have sent {notifications_sent} notifications."
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f"Successfully sent {notifications_sent} expiry notifications.")
                )
                
        except Exception as e:
            raise CommandError(f"Command failed: {str(e)}")
    
    @transaction.atomic
    def process_expiry_notifications(self, days_ahead, dry_run, force):
        """Main logic for processing expiry notifications"""
        
        # Use the custom manager method
        expiring_donations = Donation.objects.expiring_within(days=days_ahead)
        
        self.stdout.write(f"Found {expiring_donations.count()} donations expiring within {days_ahead} days")
        
        if not expiring_donations.exists():
            self.stdout.write("No expiring donations found.")
            return 0
        
        notifications_sent = 0
        email_batch = []  # For batch email sending
        
        for donation in expiring_donations:
            days_until_expiry = donation.days_until_expiry
            
            # Skip if already expired (safety check)
            if days_until_expiry < 0:
                continue
            
            recipients = self.get_notification_recipients(donation)
            
            for recipient_email in recipients:
                should_send = force or not self.alert_already_sent(
                    donation, days_until_expiry, recipient_email
                )
                
                if not should_send:
                    self.stdout.write(
                        f"  Skipping {donation.name} for {recipient_email} - already notified"
                    )
                    continue
                
                if dry_run:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  [DRY RUN] Would send {donation.urgency_level.upper()} alert for "
                            f"'{donation.name}' (expires in {days_until_expiry} days) to {recipient_email}"
                        )
                    )
                    notifications_sent += 1
                else:
                    # Prepare email for batch sending
                    email_data = self.prepare_email(donation, recipient_email, days_until_expiry)
                    email_batch.append(email_data)
                    
                    # Record the alert (with duplicate protection)
                    ExpiryAlert.objects.get_or_create(
                        donation=donation,
                        days_before_expiry=days_until_expiry,
                        recipient_email=recipient_email,
                        defaults={'alert_type': 'email'}
                    )
                    notifications_sent += 1
        
        # Send emails in batch for better performance
        if email_batch and not dry_run:
            self.send_batch_emails(email_batch)
        
        return notifications_sent
    
    def get_notification_recipients(self, donation):
        """Get list of email recipients for a donation - only the donor"""
        recipients = set()
        
        # Only add the donor's email
        if donation.donor and donation.donor.email:
            recipients.add(donation.donor.email)
        
        return list(recipients)
    
    def alert_already_sent(self, donation, days_until_expiry, recipient_email):
        """Check if alert was already sent for this combination"""
        return ExpiryAlert.objects.filter(
            donation=donation,
            days_before_expiry=days_until_expiry,
            recipient_email=recipient_email
        ).exists()
    
    def prepare_email(self, donation, recipient_email, days_until_expiry):
        """Prepare email data for batch sending"""
        urgency = donation.urgency_level
        
        subject = f"{'🚨 URGENT' if urgency in ['critical', 'high'] else '⚠️'} Medicine Expiry Alert: {donation.name}"
        
        # Create urgency-based message
        if days_until_expiry == 0:
            urgency_msg = "⚠️ CRITICAL: This medicine expires TODAY!"
        elif days_until_expiry == 1:
            urgency_msg = "🚨 URGENT: This medicine expires TOMORROW!"
        elif days_until_expiry <= 3:
            urgency_msg = f"🔴 HIGH PRIORITY: This medicine expires in {days_until_expiry} days."
        else:
            urgency_msg = f"🟡 NOTICE: This medicine will expire in {days_until_expiry} days."
        
        message = f"""
Dear HealthBridge User,

{urgency_msg}

📋 Medicine Details:
• Name: {donation.name}
• Quantity: {donation.quantity}
• Expiry Date: {donation.expiry_date.strftime('%B %d, %Y')}
• Status: {donation.get_status_display()}
• Tracking Code: {donation.tracking_code}
• Urgency Level: {urgency.upper()}

🎯 Recommended Actions:
1. Use the medicine if it's for your own needs
2. Find someone who can use it before expiry
3. Update the status if it's no longer available
4. Contact us if you need assistance

💡 To prevent waste and help others, please update the medicine status in our system if it's no longer available.

Thank you for helping reduce medicine waste and supporting community health!

Best regards,
HealthBridge Team

---
This is an automated message. If you received this in error, please contact support.
        """.strip()
        
        return (
            subject,
            message,
            getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@healthbridge.com'),
            [recipient_email]
        )
    
    def send_batch_emails(self, email_batch):
        """Send emails in batch for better performance"""
        try:
            send_mass_mail(email_batch, fail_silently=False)
            self.stdout.write(f"  ✓ Sent batch of {len(email_batch)} emails")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ✗ Batch email error: {str(e)}"))
            
            # Fallback: send emails individually
            self.stdout.write("  Attempting individual email sending...")
            for subject, message, from_email, recipient_list in email_batch:
                try:
                    send_mail(subject, message, from_email, recipient_list, fail_silently=False)
                    self.stdout.write(f"    ✓ Sent individual email to {recipient_list[0]}")
                except Exception as individual_error:
                    self.stdout.write(
                        self.style.ERROR(f"    ✗ Failed to send to {recipient_list[0]}: {individual_error}")
                    )