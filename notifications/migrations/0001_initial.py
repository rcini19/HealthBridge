# Generated migration for moving Notification model to notifications app
# This migration creates the Notification table in the notifications app

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_type', models.CharField(choices=[('donation_approved', 'Donation Approved'), ('donation_rejected', 'Donation Rejected'), ('request_approved', 'Request Approved'), ('request_rejected', 'Request Rejected'), ('request_matched', 'Request Matched'), ('medicine_expiring', 'Medicine Expiring Soon'), ('system', 'System Notification')], max_length=30)),
                ('title', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('donation_id', models.IntegerField(blank=True, null=True)),
                ('request_id', models.IntegerField(blank=True, null=True)),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('read_at', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['user', '-created_at'], name='notificatio_user_id_4f5d6e_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['user', 'is_read'], name='notificatio_user_id_7a8b9c_idx'),
        ),
    ]
