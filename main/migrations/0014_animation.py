# Generated by Django 5.1.4 on 2025-01-10 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_series'),
    ]

    operations = [
        migrations.CreateModel(
            name='Animation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='عنوان انیمیشن')),
                ('release_date', models.DateField(verbose_name='تاریخ انتشار')),
                ('description', models.TextField(blank=True, null=True, verbose_name='توضیحات')),
                ('poster', models.ImageField(blank=True, null=True, upload_to='animations/', verbose_name='پوستر')),
            ],
            options={
                'verbose_name': 'انیمیشن',
                'verbose_name_plural': 'انیمیشن\u200cها',
            },
        ),
    ]
