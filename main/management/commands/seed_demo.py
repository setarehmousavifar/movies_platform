from datetime import date

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from main.models import AgeRating, Animation, Genre, Movie, Series

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed demo catalog data and an optional staff user for local/docker demos.'

    def add_arguments(self, parser):
        parser.add_argument('--with-admin', action='store_true', help='Ensure admin/admin123 exists')

    def handle(self, *args, **options):
        rating, _ = AgeRating.objects.get_or_create(name='PG-13', defaults={'description': 'Demo'})
        action, _ = Genre.objects.get_or_create(genre_name='Action', defaults={'description': 'Action'})
        drama, _ = Genre.objects.get_or_create(genre_name='Drama', defaults={'description': 'Drama'})

        movie, created = Movie.objects.get_or_create(
            title='Sample Horizon',
            defaults={
                'release_date': date(2024, 6, 1),
                'description': 'Seeded demo movie.',
                'duration': 118,
                'language': 'English',
                'country': 'USA',
                'age_rating': rating,
                'overall_rating': '8.20',
                'view_count': 42,
            },
        )
        if created:
            movie.genres.add(action, drama)

        series, created = Series.objects.get_or_create(
            title='Demo Chronicles',
            defaults={
                'start_year': 2022,
                'status': 'ongoing',
                'season_count': 2,
                'episode_count': 16,
                'release_date': date(2022, 3, 10),
                'description': 'Seeded demo series.',
                'duration': 45,
                'language': 'English',
                'country': 'USA',
                'age_rating': rating,
                'overall_rating': '8.00',
            },
        )
        if created:
            series.genres.add(action, drama)

        anim, created = Animation.objects.get_or_create(
            title='Pixel Adventure',
            defaults={
                'release_date': date(2021, 8, 20),
                'description': 'Seeded demo animation.',
                'duration': 95,
                'language': 'English',
                'country': 'Japan',
                'age_rating': rating,
                'overall_rating': '7.80',
            },
        )
        if created:
            anim.genres.add(action)

        if options['with_admin']:
            if not User.objects.filter(username='admin').exists():
                User.objects.create_superuser(
                    username='admin',
                    email='admin@example.com',
                    password='admin123',
                )
                self.stdout.write(self.style.SUCCESS('Created admin / admin123'))
            else:
                self.stdout.write('Admin user already exists')

        self.stdout.write(self.style.SUCCESS('Demo catalog seed complete.'))
