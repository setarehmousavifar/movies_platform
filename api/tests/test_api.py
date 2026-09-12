from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from main.models import AgeRating, DownloadLink, Genre, Movie, Notification
from main.services import SubscriptionService

User = get_user_model()


class ApiCatalogTests(APITestCase):
    def setUp(self):
        rating = AgeRating.objects.create(name='G')
        genre = Genre.objects.create(genre_name='Drama')
        self.movie = Movie.objects.create(
            title='API Movie',
            release_date=date(2023, 5, 1),
            description='api desc',
            duration=90,
            language='English',
            country='USA',
            age_rating=rating,
            overall_rating='7.50',
        )
        self.movie.genres.add(genre)
        self.link = DownloadLink.objects.create(
            movie=self.movie,
            quality='720p',
            download_url='https://cdn.example.com/secret.mp4',
            file_size='1GB',
        )

    def test_movies_list(self):
        url = reverse('api-movies-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['count'], 1)

    def test_search(self):
        url = reverse('api-search')
        response = self.client.get(url, {'q': 'API'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(item['title'] == 'API Movie' for item in response.data))

    def test_recommendations(self):
        url = reverse('api-recommendations')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(item['title'] == 'API Movie' for item in response.data))

    def test_recommendations_bad_limit(self):
        response = self.client.get(reverse('api-recommendations'), {'limit': 'abc'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('code'), 'validation_error')

    def test_detail_hides_download_url(self):
        response = self.client.get(reverse('api-movies-detail', args=[self.movie.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        links = response.data['download_links']
        self.assertEqual(len(links), 1)
        self.assertNotIn('download_url', links[0])
        self.assertTrue(links[0]['locked'])
        self.assertIn('/api/v1/downloads/', links[0]['unlock_path'])

    def test_healthz(self):
        response = self.client.get('/healthz')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['database'], 'up')


class ApiAuthEngagementTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='apiuser', email='apiuser@example.com', password='TestPass123!'
        )
        rating = AgeRating.objects.create(name='PG-13')
        self.movie = Movie.objects.create(
            title='Fav Movie',
            release_date=date(2022, 1, 1),
            description='d',
            duration=80,
            language='English',
            country='USA',
            age_rating=rating,
        )
        self.link = DownloadLink.objects.create(
            movie=self.movie,
            quality='1080p',
            download_url='https://cdn.example.com/premium.mp4',
            file_size='2GB',
        )
        refresh = RefreshToken.for_user(self.user)
        self.refresh = str(refresh)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_me(self):
        response = self.client.get(reverse('api-me'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'apiuser')

    def test_token_obtain(self):
        self.client.credentials()
        response = self.client.post(
            reverse('api-token'),
            {'username': 'apiuser', 'password': 'TestPass123!'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_logout_blacklists_refresh(self):
        response = self.client.post(
            reverse('api-logout'), {'refresh': self.refresh}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        refresh_resp = self.client.post(
            reverse('api-token-refresh'), {'refresh': self.refresh}, format='json'
        )
        self.assertEqual(refresh_resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_favorite_create_idempotent(self):
        url = reverse('api-favorites-list')
        r1 = self.client.post(url, {'movie': self.movie.pk}, format='json')
        r2 = self.client.post(url, {'movie': self.movie.pk}, format='json')
        self.assertIn(r1.status_code, (status.HTTP_200_OK, status.HTTP_201_CREATED))
        self.assertEqual(r2.status_code, status.HTTP_200_OK)

    def test_favorite_requires_exactly_one_target(self):
        response = self.client.post(reverse('api-favorites-list'), {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_watchlist_create(self):
        response = self.client.post(
            reverse('api-watchlist-list'), {'movie': self.movie.pk}, format='json'
        )
        self.assertIn(response.status_code, (status.HTTP_200_OK, status.HTTP_201_CREATED))

    def test_review_create(self):
        response = self.client.post(
            reverse('api-reviews-list'),
            {'movie': self.movie.pk, 'rating': 8, 'review_text': 'solid'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_download_unlock_forbidden_for_free_user(self):
        response = self.client.get(reverse('api-download-unlock', args=[self.link.pk]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get('code'), 'permission_denied')

    def test_download_unlock_ok_for_premium(self):
        staff = User.objects.create_user(
            username='staffer',
            email='staff@example.com',
            password='TestPass123!',
            is_staff=True,
        )
        SubscriptionService.assign(
            user=self.user,
            actor=staff,
            subscription_type='premium',
            end_date=date.today() + timedelta(days=30),
        )
        response = self.client.get(reverse('api-download-unlock', args=[self.link.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['download_url'], self.link.download_url)

    def test_subscription_me(self):
        response = self.client.get(reverse('api-subscription-me'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('can_download', response.data)

    def test_notifications_list(self):
        Notification.objects.create(user=self.user, message='hello')
        response = self.client.get(reverse('api-notifications'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_register(self):
        self.client.credentials()
        response = self.client.post(
            reverse('api-register'),
            {
                'username': 'newbie',
                'email': 'newbie@example.com',
                'password': 'TestPass123!',
                'password_confirm': 'TestPass123!',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class ApiStaffEnrichTests(APITestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username='boss',
            email='boss@example.com',
            password='TestPass123!',
            is_staff=True,
        )
        rating = AgeRating.objects.create(name='R')
        self.movie = Movie.objects.create(
            title='Enrich Me',
            release_date=date(2021, 1, 1),
            description='A daring crew explores danger beyond the stars.',
            duration=100,
            language='English',
            country='USA',
            age_rating=rating,
        )
        refresh = RefreshToken.for_user(self.staff)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_enrich_staff_only(self):
        response = self.client.post(
            reverse('api-movie-enrich', args=[self.movie.pk]),
            {'force': True},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get('ai_summary'))
