# Generated by Django 4.2.2 on 2023-07-13 12:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modelCore', '0008_alter_chatroomusership_chatroom'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatroom',
            name='update_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
