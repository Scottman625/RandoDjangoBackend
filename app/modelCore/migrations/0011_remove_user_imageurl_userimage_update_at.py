# Generated by Django 4.2.2 on 2023-07-20 01:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modelCore', '0010_remove_user_image_alter_chatroommessage_create_at_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='imageUrl',
        ),
        migrations.AddField(
            model_name='userimage',
            name='update_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]