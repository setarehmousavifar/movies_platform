# Generated by Django 5.1.4 on 2025-01-24 07:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0021_alter_profile_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='subscription_type',
            field=models.CharField(choices=[('basic', 'Basic'), ('premium', 'Premium')], default='basic', max_length=50),
        ),
    ]
