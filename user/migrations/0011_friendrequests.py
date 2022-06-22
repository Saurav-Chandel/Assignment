# Generated by Django 4.0.5 on 2022-06-06 10:02

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0010_user_is_phone_verified'),
    ]

    operations = [
        migrations.CreateModel(
            name='FriendRequests',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Status', models.CharField(choices=[('Sent', 'Sent'), ('Accept', 'Accept'), ('Reject', 'Reject')], default='Sent', max_length=200)),
                ('DateAdded', models.DateTimeField(default=django.utils.timezone.now)),
                ('Receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Receiver', to='user.profiles')),
                ('Sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Sender', to='user.profiles')),
            ],
            options={
                'ordering': ['-DateAdded'],
                'unique_together': {('Sender', 'Receiver')},
            },
        ),
    ]
