from django.conf import settings
from django.db import migrations, models

from django.contrib.postgres.operations import TrigramExtension

class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('socialuser', '0001_initial'),
    ]

    operations = [
        TrigramExtension()
    ]