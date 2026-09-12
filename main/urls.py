from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('movies/', views.movie_list, name='movie_list'),
    path('movies/<int:pk>/', views.movie_detail, name='movie_detail'),
    path('series/', views.series_list, name='series_list'),
    path('series/<int:pk>/', views.series_detail, name='series_detail'),
    path('animations/', views.animation_list, name='animation_list'),
    path('animations/<int:pk>/', views.animation_detail, name='animation_detail'),
    path('top-movies/', views.top_movies, name='top_movies'),
    path('top-series/', views.top_series, name='top_series'),

    path('subscription/', views.subscription, name='subscription'),
    path('update-subscription/', views.update_subscription, name='update_subscription'),
    path(
        'subscription/request-upgrade/',
        views.request_premium_upgrade,
        name='request_premium_upgrade',
    ),
    path('subscription/mock-checkout/', views.mock_checkout, name='mock_checkout'),

    path('watchlist/', views.watchlist_view, name='watchlist'),
    path('watchlist/add/<int:movie_id>/', views.add_to_watchlist, name='add_to_watchlist'),
    path(
        'watchlist/remove/<int:movie_id>/',
        views.remove_from_watchlist,
        name='remove_from_watchlist',
    ),

    path('favorites/add/<int:movie_id>/', views.add_to_favorites, name='add_to_favorites'),
    path(
        'favorites/remove/<int:movie_id>/',
        views.remove_from_favorites,
        name='remove_from_favorites',
    ),
    path('favorites/', views.favorites_list, name='favorites_list'),
    path('notifications/', views.notifications_list, name='notifications_list'),
    path(
        'notifications/<int:pk>/read/',
        views.notification_mark_read,
        name='notification_mark_read',
    ),

    path('search/', views.search, name='search'),
    path('movies/advanced-search/', views.movie_advanced_search, name='movie_advanced_search'),
    path('series/advanced-search/', views.series_advanced_search, name='series_advanced_search'),
    path(
        'animations/advanced-search/',
        views.animation_advanced_search,
        name='animation_advanced_search',
    ),
    path('filter/', views.filter_movies, name='filter_movies'),

    path('genres/', views.genre_list, name='genre_list'),
    path('genres/<int:genre_id>/', views.movies_by_genre, name='movies_by_genre'),

    path('profile/', views.profile_view, name='profile'),
    path('register/', views.register_user, name='register'),
]
