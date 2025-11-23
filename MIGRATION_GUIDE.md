# Migration Instructions for Moving Notification Model

## Overview
The Notification model has been moved from `healthbridge_app` to the new `notifications` app.

## Migration Steps

### Option 1: If You Have Existing Notification Data (Production/Staging)

Since the Notification model already exists in the database (from healthbridge_app), you need to:

1. **Do NOT run migrations yet**. First, manually update the django_content_type table:

```sql
-- Update the content type reference for Notification model
UPDATE django_content_type 
SET app_label = 'notifications' 
WHERE app_label = 'healthbridge_app' AND model = 'notification';
```

2. **Run this command to fake the initial migration for notifications app:**
```bash
python manage.py migrate notifications 0001_initial --fake
```

3. **Create a migration to remove the Notification model from healthbridge_app:**
```bash
python manage.py makemigrations healthbridge_app --empty
```

Then edit the generated migration file to add:
```python
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('healthbridge_app', '<previous_migration>'),
    ]
    
    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name='notification',
                    name='user',
                ),
                migrations.DeleteModel(
                    name='Notification',
                ),
            ],
            database_operations=[],
        ),
    ]
```

4. **Run the migration:**
```bash
python manage.py migrate
```

### Option 2: If You Have NO Existing Data (Fresh Development)

1. **Delete the old healthbridge_app Notification migration:**
   - Find and delete `healthbridge_app/migrations/0008_notification.py` (or whichever migration created Notification)

2. **Delete the SQLite database:**
```bash
del db.sqlite3
```

3. **Run migrations from scratch:**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### Option 3: Data Migration (Safest for Production)

Create a data migration to copy data:

```bash
python manage.py makemigrations notifications
python manage.py migrate notifications 0001_initial --fake
python manage.py makemigrations healthbridge_app --empty
```

Edit the migration file:
```python
from django.db import migrations

def copy_notifications(apps, schema_editor):
    # This operation does nothing because tables are the same
    pass

def reverse_copy(apps, schema_editor):
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('healthbridge_app', '<previous_migration>'),
        ('notifications', '0001_initial'),
    ]
    
    operations = [
        migrations.RunPython(copy_notifications, reverse_copy),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(model_name='notification', name='user'),
                migrations.DeleteModel(name='Notification'),
            ],
            database_operations=[],
        ),
    ]
```

## Verification

After migration, verify:

1. **Check the database:**
```bash
python manage.py dbshell
.tables
.schema healthbridge_app_notification
```

2. **Test notifications:**
```python
python manage.py shell
from notifications.models import Notification
print(Notification.objects.count())
```

3. **Test the admin interface:**
   - Login to /admin/
   - Check that notifications appear under "Notifications" app

## Rollback Plan

If issues occur:
1. Revert code changes
2. Run: `python manage.py migrate healthbridge_app <previous_migration>`
3. Run: `python manage.py migrate notifications zero`

## Notes

- The database table name remains `healthbridge_app_notification` unless explicitly changed
- All existing data will be preserved with Option 1 and Option 3
- Foreign key relationships remain intact
- Update any raw SQL queries to use the correct table name
