# Generated manually to add REQUEST_CREATED notification type

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(
                choices=[
                    ('donation_approved', 'Donation Approved'),
                    ('donation_rejected', 'Donation Rejected'),
                    ('request_approved', 'Request Approved'),
                    ('request_rejected', 'Request Rejected'),
                    ('request_created', 'Request Created'),
                    ('request_matched', 'Request Matched'),
                    ('medicine_expiring', 'Medicine Expiring Soon'),
                    ('system', 'System Notification')
                ],
                max_length=30
            ),
        ),
    ]
