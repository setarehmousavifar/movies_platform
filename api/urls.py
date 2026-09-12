from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AnimationViewSet,
    EnrichAnimationView,
    EnrichMovieView,
    EnrichSeriesView,
    FavoriteViewSet,
    GenreViewSet,
    MeView,
    MovieViewSet,
    NotificationListView,
    NotificationMarkReadView,
    RecommendationView,
    RegisterView,
    ReviewViewSet,
    SearchView,
    SeriesViewSet,
    SubscriptionMeView,
    SubscriptionRequestUpgradeView,
    ThrottledTokenObtainPairView,
    ThrottledTokenRefreshView,
    WatchlistViewSet,
)

router = DefaultRouter()
router.register('movies', MovieViewSet, basename='api-movies')
router.register('series', SeriesViewSet, basename='api-series')
router.register('animations', AnimationViewSet, basename='api-animations')
router.register('genres', GenreViewSet, basename='api-genres')
router.register('reviews', ReviewViewSet, basename='api-reviews')
router.register('favorites', FavoriteViewSet, basename='api-favorites')
router.register('watchlist', WatchlistViewSet, basename='api-watchlist')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='api-register'),
    path('auth/token/', ThrottledTokenObtainPairView.as_view(), name='api-token'),
    path('auth/token/refresh/', ThrottledTokenRefreshView.as_view(), name='api-token-refresh'),
    path('auth/me/', MeView.as_view(), name='api-me'),
    path('subscriptions/me/', SubscriptionMeView.as_view(), name='api-subscription-me'),
    path(
        'subscriptions/request-upgrade/',
        SubscriptionRequestUpgradeView.as_view(),
        name='api-subscription-request',
    ),
    path('search/', SearchView.as_view(), name='api-search'),
    path('recommendations/', RecommendationView.as_view(), name='api-recommendations'),
    path('movies/<int:pk>/enrich/', EnrichMovieView.as_view(), name='api-movie-enrich'),
    path('series/<int:pk>/enrich/', EnrichSeriesView.as_view(), name='api-series-enrich'),
    path(
        'animations/<int:pk>/enrich/',
        EnrichAnimationView.as_view(),
        name='api-animation-enrich',
    ),
    path('notifications/', NotificationListView.as_view(), name='api-notifications'),
    path(
        'notifications/<int:pk>/read/',
        NotificationMarkReadView.as_view(),
        name='api-notification-read',
    ),
    path('', include(router.urls)),
]
