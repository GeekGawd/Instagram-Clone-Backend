# Generated by Django 3.2.11 on 2022-01-20 06:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('socialuser', '0008_alter_story_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='story',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='userstory', to=settings.AUTH_USER_MODEL),
        ),
    ]