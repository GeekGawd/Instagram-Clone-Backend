# Generated by Django 4.0 on 2021-12-26 07:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_remove_user_bio_remove_user_profile_photo'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_photo', models.ImageField(null=True, upload_to='')),
                ('bio', models.CharField(max_length=150, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.user')),
            ],
        ),
    ]
