from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views

urlpatterns = [
    # General Pages
    path('', views.home, name='home'),  # صفحه اصلی
    path('movies/', views.movie_list, name='movie_list'),  # لیست فیلم‌ها
    path('movies/<int:pk>/', views.movie_detail, name='movie_detail'),  # جزئیات فیلم
    path('series/', views.series_list, name='series_list'),
    path('series/<int:pk>/', views.series_detail, name='series_detail'),
    path('animations/', views.animation_list, name='animation_list'),
    path('animations/<int:pk>/', views.animation_detail, name='animation_detail'),
    path('top-movies/', views.top_movies, name='top_movies'),
    path('top-series/', views.top_series, name='top_series'),
    
    path('subscription-settings/', views.subscription_settings, name='subscription_settings'),

    # Watchlist 
    path('watchlist/', views.watchlist_view, name='watchlist'),
    path('watchlist/add/<int:movie_id>/', views.add_to_watchlist, name='add_to_watchlist'),
    path('watchlist/remove/<int:movie_id>/', views.remove_from_watchlist, name='remove_from_watchlist'),

    # Favorites
    path('favorites/add/<int:movie_id>/', views.add_to_favorites, name='add_to_favorites'),
    path('favorites/remove/<int:movie_id>/', views.remove_from_favorites, name='remove_from_favorites'),
    path('favorites/', views.favorites_list, name='favorites_list'),

     # Search and Filters
    path('search/', views.search, name='search'),
    path('advanced-search/', views.advanced_search, name='advanced_search'),  # جستجوی پیشرفته
    path('filter/', views.filter_movies, name='filter_movies'),

    # Genres
    path('genres/', views.genre_list, name='genre_list'),  # لیست ژانرها
    path('genres/<int:genre_id>/', views.movies_by_genre, name='movies_by_genre'),  # فیلم‌ها بر اساس ژانر

    # User Pages
    path('profile/', views.profile_view, name='profile'),  # صفحه پروفایل
    path('register/', views.register_user, name='register'),  # ثبت‌نام
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),  #خروج
    path('login/', views.custom_login_view, name='login'), 
]
