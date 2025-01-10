from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import User, Movie, Review, Genre, FavoriteMovie
from django.db.models import Q, Avg
from .forms import UserRegistrationForm, ProfileUpdateForm, ReviewForm
from .models import Profile

# ========================
# ثبت‌نام کاربر
# ========================
def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # رمز عبور را هش کنید
            user.save()
            login(request, user)  # ورود خودکار پس از ثبت‌نام
            messages.success(request, "Registration successful. Welcome!")
            return redirect('home')  # هدایت به صفحه اصلی یا هر صفحه دیگر
        else:
            messages.error(request, "There was an error with your registration. Please try again.")
    else:
        form = UserRegistrationForm()

    return render(request, 'main/register.html', {'form': form})

# ========================
# پروفایل کاربر
# ========================
@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile')  # Redirect to the profile page after saving
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'main/profile.html', {'form': form})


# ========================
# لاگ این
# ========================
def custom_login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You have logged in successfully!")
            return redirect('home')  # یا هر صفحه‌ای که می‌خواهی کاربر پس از ورود منتقل شود
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')
    else:
        return render(request, 'main/login.html')


# ========================
# لاگ‌اوت
# ========================
def custom_logout(request):
    logout(request)
    messages.success(request, "با موفقیت خارج شدید!")
    return redirect('home')


# ========================
# صفحه اصلی
# ========================
def home(request):
    new_movies = Movie.objects.all().order_by('-release_date')[:5]
    popular_movies = Movie.objects.all().order_by('-view_count')[:5]
    return render(request, 'main/home.html', {
        'new_movies': new_movies,
        'popular_movies': popular_movies,
    })


# ========================
# جزئیات هر فیلم
# ========================
@login_required
def movie_detail(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    reviews = Review.objects.filter(movie=movie, parent__isnull=True)

    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = movie.favorites.filter(id=request.user.id).exists()

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.movie = movie
            review.user = request.user
            parent_id = request.POST.get('parent_id')  # دریافت parent_id از فرم
            if parent_id:
                try:
                    parent_review = Review.objects.get(id=parent_id)
                    review.parent = parent_review
                except Review.DoesNotExist:
                    pass
            review.save()
            return redirect('movie_detail', pk=pk)
    else:
        form = ReviewForm()

    return render(request, 'main/movie_detail.html', {
        'movie': movie,
        'reviews': reviews,
        'form': form,
        'is_favorite': is_favorite,
    })


# ========================
# لیست علاقه‌مندی‌ها
# ========================
@login_required
def add_to_favorites(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    FavoriteMovie.objects.get_or_create(user=request.user, movie=movie)
    return redirect('favorites_list')

@login_required
def remove_from_favorites(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    favorite = FavoriteMovie.objects.filter(user=request.user, movie=movie)
    if favorite.exists():
        favorite.delete()
    return redirect('favorites_list')

@login_required
def favorites_list(request):
    favorites = FavoriteMovie.objects.filter(user=request.user).select_related('movie')
    return render(request, 'main/favorites_list.html', {'favorites': favorites})


# ========================
# جستجوی ساده
# ========================
def search_movies(request):
    query = request.GET.get('q', '')
    movies = Movie.objects.filter(Q(title__icontains=query) | Q(language__icontains=query)) if query else []
    return render(request, 'main/search_results.html', {'movies': movies, 'query': query})


# ========================
# جستجوی پیشرفته
# ========================
def advanced_search(request):
    query = request.GET.get('query', '')
    genre_name = request.GET.get('genre', '')
    language = request.GET.get('language', '')
    min_rating = request.GET.get('min_rating', '')

    movies = Movie.objects.all()

    if query:
        movies = movies.filter(Q(title__icontains=query) | Q(description__icontains=query))

    if genre_name:
        movies = movies.filter(genres__genre__genre_name__icontains=genre_name)

    if language:
        movies = movies.filter(language__icontains=language)

    if min_rating:
        movies = movies.filter(overall_rating__gte=min_rating)

    genres = Genre.objects.all()

    context = {
        'movies': movies,
        'query': query,
        'genres': genres,
    }
    return render(request, 'main/advanced_search.html', context)


# ========================
# نمایش فیلم‌ها بر اساس ژانر
# ========================
def movies_by_genre(request, genre_id):
    genre = get_object_or_404(Genre, id=genre_id)
    movies = genre.movie_set.all()
    return render(request, 'main/movies_by_genre.html', {'genre': genre, 'movies': movies})


# ========================
# لیست همه فیلم‌ها
# ========================
def movie_list(request):
    movies = Movie.objects.all()  # همه فیلم‌ها را از دیتابیس دریافت می‌کند
    return render(request, 'main/movie_list.html', {'movies': movies})


# ========================
# فیلتر فیلم‌ها
# ========================
def filter_movies(request):
    genre = request.GET.get('genre')
    language = request.GET.get('language')
    min_rating = request.GET.get('min_rating')

    movies = Movie.objects.all()
    if genre:
        movies = movies.filter(genres__genre__genre_name__iexact=genre)
    if language:
        movies = movies.filter(language__iexact=language)
    if min_rating:
        movies = movies.annotate(avg_rating=Avg('review__rating')).filter(avg_rating__gte=min_rating)

    genres = Genre.objects.all()

    context = {
        'movies': movies,
        'genres': genres,
        'selected_genre': genre,
        'selected_language': language,
        'selected_min_rating': min_rating,
    }
    return render(request, 'main/filter_movies.html', context)


# ========================
# نمایش همه ژانرها
# ========================
def genre_list(request):
    genres = Genre.objects.all()
    return render(request, 'main/genre_list.html', {'genres': genres})