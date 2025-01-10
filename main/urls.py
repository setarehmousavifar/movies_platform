from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views

urlpatterns = [
    # General Pages
    path('', views.home, name='home'),  # صفحه اصلی
    path('movies/', views.movie_list, name='movie_list'),  # لیست فیلم‌ها
    path('movies/<int:pk>/', views.movie_detail, name='movie_detail'),  # جزئیات فیلم

    # Favorites
    path('favorites/add/<int:movie_id>/', views.add_to_favorites, name='add_to_favorites'),
    path('favorites/remove/<int:movie_id>/', views.remove_from_favorites, name='remove_from_favorites'),
    path('favorites/', views.favorites_list, name='favorites_list'),

     # Search and Filters
    path('search/', views.search_movies, name='search_movies'),
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
