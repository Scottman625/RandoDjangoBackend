# Generated by Django 4.2.2 on 2023-07-20 01:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modelCore', '0011_remove_user_imageurl_userimage_update_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='image',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]