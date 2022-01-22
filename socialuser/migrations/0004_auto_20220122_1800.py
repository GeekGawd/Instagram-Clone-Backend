# Generated by Django 3.2.11 on 2022-01-22 12:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('socialuser', '0003_remove_image_story_remove_video_story_story_content'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='story',
            name='content',
        ),
        migrations.AddField(
            model_name='image',
            name='story',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='socialuser.story'),
        ),
        migrations.AddField(
            model_name='video',
            name='story',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='socialuser.story'),
        ),
    ]
