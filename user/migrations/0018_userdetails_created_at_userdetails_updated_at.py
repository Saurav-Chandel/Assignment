# Generated by Django 4.0.5 on 2022-06-14 06:01

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0017_alter_form_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdetails',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='userdetails',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
