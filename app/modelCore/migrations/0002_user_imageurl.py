# Generated by Django 4.2.2 on 2023-07-04 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modelCore', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='imageUrl',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
