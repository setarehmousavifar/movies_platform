# Generated by Django 5.1.4 on 2025-01-11 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_series_end_year_series_episodes_series_seasons_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='directors',
            field=models.ManyToManyField(related_name='movies', to='main.director', verbose_name='کارگردان\u200cها'),
        ),
        migrations.AddField(
            model_name='movie',
            name='stars',
            field=models.ManyToManyField(related_name='movies', to='main.actor', verbose_name='بازیگران'),
        ),
        migrations.AddField(
            model_name='series',
            name='directors',
            field=models.ManyToManyField(related_name='series', to='main.director', verbose_name='کارگردان\u200cها'),
        ),
        migrations.AddField(
            model_name='series',
            name='stars',
            field=models.ManyToManyField(related_name='series', to='main.actor', verbose_name='بازیگران'),
        ),
    ]