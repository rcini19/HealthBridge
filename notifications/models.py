from django.db import models
from django.conf import settings
from django.utils import timezone


class Notification(models.Model):
    """User notifications for approvals, rejections, and system updates"""
    
    class Type(models.TextChoices):
        DONATION_APPROVED = 'donation_approved', 'Donation Approved'
        DONATION_REJECTED = 'donation_rejected', 'Donation Rejected'
        REQUEST_APPROVED = 'request_approved', 'Request Approved'
        REQUEST_REJECTED = 'request_rejected', 'Request Rejected'
        REQUEST_MATCHED = 'request_matched', 'Request Matched'
        MEDICINE_EXPIRING = 'medicine_expiring', 'Medicine Expiring Soon'
        SYSTEM = 'system', 'System Notification'
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(
        max_length=30,
        choices=Type.choices
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Optional references
    donation_id = models.IntegerField(null=True, blank=True)
    request_id = models.IntegerField(null=True, blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'healthbridge_app_notification'  # Keep using the existing table name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
        ]
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    def __str__(self):
        return f"{self.user.email} - {self.title}"
    
    @property
    def time_ago(self):
        """Human-readable time since notification was created"""
        delta = timezone.now() - self.created_at
        
        if delta.days > 0:
            return f"{delta.days} day{'s' if delta.days > 1 else ''} ago"
        elif delta.seconds >= 3600:
            hours = delta.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif delta.seconds >= 60:
            minutes = delta.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"
