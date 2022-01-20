# Generated by Django 3.2.11 on 2022-01-20 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socialuser', '0010_rename_profile_story_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='story',
            old_name='is_expired',
            new_name='is_seen',
        ),
        migrations.AlterField(
            model_name='story',
            name='content',
            field=models.URLField(),
        ),
    ]
