# Generated manually for Phase 0 stabilization

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0025_downloadlink_animation_downloadlink_series'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='movie',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='main.movie',
                verbose_name='فیلم',
            ),
        ),
        migrations.AlterField(
            model_name='downloadlink',
            name='movie',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='download_links',
                to='main.movie',
            ),
        ),
        migrations.AlterUniqueTogether(
            name='favoritemovie',
            unique_together={('user', 'movie')},
        ),
    ]
