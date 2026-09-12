from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase

from main.exceptions import PermissionDeniedError
from main.models import AgeRating, Genre, Movie, Subscription
from main.services import EntitlementService, FavoriteService, SubscriptionService, ViewCountService

User = get_user_model()


class SubscriptionServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='member', email='member@example.com', password='TestPass123!'
        )
        self.staff = User.objects.create_user(
            username='staffer',
            email='staff@example.com',
            password='TestPass123!',
            is_staff=True,
        )

    def test_user_cannot_self_assign_premium(self):
        with self.assertRaises(PermissionDeniedError):
            SubscriptionService.assign(
                user=self.user,
                actor=self.user,
                subscription_type='premium',
                end_date=date.today() + timedelta(days=30),
            )

    def test_staff_can_assign_premium_and_sync_flag(self):
        sub = SubscriptionService.assign(
            user=self.user,
            actor=self.staff,
            subscription_type='premium',
            end_date=date.today() + timedelta(days=30),
        )
        self.user.refresh_from_db()
        self.assertTrue(self.user.has_premium_access())
        self.assertTrue(self.user.is_premium)
        self.assertEqual(sub.subscription_type, 'premium')
        self.assertTrue(EntitlementService.can_download(self.user))

    def test_upgrade_request_does_not_grant_premium(self):
        SubscriptionService.request_upgrade(user=self.user, note='please')
        self.user.refresh_from_db()
        self.assertFalse(self.user.has_premium_access())


class CatalogServiceTests(TestCase):
    def setUp(self):
        self.rating = AgeRating.objects.create(name='PG')
        self.genre = Genre.objects.create(genre_name='Action')
        self.movie = Movie.objects.create(
            title='Test Film',
            release_date=date(2024, 1, 1),
            description='desc',
            duration=100,
            language='English',
            country='USA',
            age_rating=self.rating,
            overall_rating='8.00',
        )
        self.movie.genres.add(self.genre)
        self.user = User.objects.create_user(
            username='fan', email='fan@example.com', password='TestPass123!'
        )

    def test_view_count_bump(self):
        ViewCountService.bump(Movie, self.movie.pk)
        self.movie.refresh_from_db()
        self.assertEqual(self.movie.view_count, 1)

    def test_favorite_idempotent(self):
        item1, created1 = FavoriteService.add_movie(self.user, self.movie)
        item2, created2 = FavoriteService.add_movie(self.user, self.movie)
        self.assertTrue(created1)
        self.assertFalse(created2)
        self.assertEqual(item1.pk, item2.pk)
