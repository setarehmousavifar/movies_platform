from datetime import date

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from main.models import AgeRating, Genre, Movie

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
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_me(self):
        response = self.client.get(reverse('api-me'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'apiuser')

    def test_favorite_create_idempotent(self):
        url = reverse('api-favorites-list')
        r1 = self.client.post(url, {'movie': self.movie.pk}, format='json')
        r2 = self.client.post(url, {'movie': self.movie.pk}, format='json')
        self.assertIn(r1.status_code, (status.HTTP_200_OK, status.HTTP_201_CREATED))
        self.assertEqual(r2.status_code, status.HTTP_200_OK)

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
