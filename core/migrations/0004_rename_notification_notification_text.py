# Generated by Django 4.0 on 2022-01-14 11:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_notification_date_notification_is_seen_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='notification',
            old_name='notification',
            new_name='text',
        ),
    ]
