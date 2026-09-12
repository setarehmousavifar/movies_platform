from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from main.models import AgeRating, Genre, Movie, Notification
from main.services import AlertService, EnrichmentService, RecommendationService, SearchService

User = get_user_model()


@override_settings(CATALOG_ALERTS_ENABLED=False)
class Phase5ServiceTests(TestCase):
    def setUp(self):
        self.rating = AgeRating.objects.create(name='PG')
        self.genre = Genre.objects.create(genre_name='Sci-Fi')
        self.movie = Movie.objects.create(
            title='Nebula Rising',
            release_date=date(2024, 6, 1),
            description=(
                'A daring crew explores a distant nebula. Danger awaits beyond the stars. '
                'Friendship and courage decide their fate.'
            ),
            duration=110,
            language='English',
            country='USA',
            age_rating=self.rating,
            overall_rating='8.20',
        )
        self.movie.genres.add(self.genre)
        self.user = User.objects.create_user(
            username='reco', email='reco@example.com', password='TestPass123!'
        )

    def test_search_finds_description(self):
        results = SearchService.search_all('nebula')
        titles = [r['title'] for r in results]
        self.assertIn('Nebula Rising', titles)

    def test_local_enrichment(self):
        EnrichmentService.enrich_instance(self.movie, force=True)
        self.movie.refresh_from_db()
        self.assertTrue(self.movie.ai_summary)
        self.assertTrue(self.movie.ai_tags)
        self.assertIsNotNone(self.movie.ai_enriched_at)

    def test_recommendations_exclude_favorites(self):
        from main.services import FavoriteService

        FavoriteService.add_movie(self.user, self.movie)
        other = Movie.objects.create(
            title='Other Film',
            release_date=date(2023, 1, 1),
            description='space adventure nebula',
            duration=90,
            language='English',
            country='USA',
            age_rating=self.rating,
            overall_rating='7.00',
        )
        other.genres.add(self.genre)
        recs = RecommendationService.recommend_movies(self.user, limit=10)
        ids = [m.id for m in recs]
        self.assertNotIn(self.movie.id, ids)
        self.assertIn(other.id, ids)

    def test_alert_staff_only(self):
        staff = User.objects.create_user(
            username='boss',
            email='boss@example.com',
            password='TestPass123!',
            is_staff=True,
        )
        AlertService.notify_breaking('X', 'movie', self.movie.pk, message='hello staff')
        self.assertTrue(Notification.objects.filter(user=staff, message='hello staff').exists())
        self.assertFalse(Notification.objects.filter(user=self.user).exists())
