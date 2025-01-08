# Generated by Django 5.1.4 on 2025-01-08 13:23

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_actor_genre_movie_movieactor_moviegenre'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='country',
            field=models.CharField(default='Unknown', max_length=100, verbose_name='کشور تولید'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='movie',
            name='overall_rating',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=3, verbose_name='امتیاز کلی'),
        ),
        migrations.CreateModel(
            name='FavoriteMovie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.movie', verbose_name='فیلم')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='کاربر')),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(verbose_name='پیام اعلان')),
                ('sent_date', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ارسال')),
                ('is_read', models.BooleanField(default=False, verbose_name='خوانده شده')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='کاربر')),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveIntegerField(verbose_name='امتیاز')),
                ('review_text', models.TextField(blank=True, null=True, verbose_name='متن نقد')),
                ('review_date', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ نقد')),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.movie', verbose_name='فیلم')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='کاربر')),
            ],
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subscription_type', models.CharField(choices=[('basic', 'عادی'), ('premium', 'پریمیوم')], max_length=50, verbose_name='نوع اشتراک')),
                ('start_date', models.DateField(verbose_name='تاریخ شروع')),
                ('end_date', models.DateField(verbose_name='تاریخ پایان')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='کاربر')),
            ],
        ),
        migrations.CreateModel(
            name='WalletTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_type', models.CharField(choices=[('credit', 'شارژ'), ('debit', 'برداشت')], max_length=50, verbose_name='نوع تراکنش')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='مبلغ تراکنش')),
                ('transaction_date', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ تراکنش')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='کاربر')),
            ],
        ),
        migrations.CreateModel(
            name='WatchHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('watch_datetime', models.DateTimeField(auto_now_add=True, verbose_name='زمان تماشا')),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.movie', verbose_name='فیلم')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='کاربر')),
            ],
        ),
    ]
