# Generated by Django 4.2.2 on 2023-07-12 16:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('modelCore', '0007_rename_user_chatroommessage_sender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatroomusership',
            name='chatroom',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chatroom_usership', to='modelCore.chatroom'),
        ),
    ]