from django.db import migrations
from django.contrib.postgres.operations import TrigramExtension

class Migration(migrations.Migration):

    dependencies = [
        ('socialuser', '0022_auto_20220117_1913'),
    ]

    operations = [
        TrigramExtension()
    ]