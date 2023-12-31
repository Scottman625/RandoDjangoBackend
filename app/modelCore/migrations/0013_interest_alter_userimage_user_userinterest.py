# Generated by Django 4.2.2 on 2023-07-21 03:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('modelCore', '0012_user_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Interest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interest', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='userimage',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='UserInterest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interest', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='modelCore.interest')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
