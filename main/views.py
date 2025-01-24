from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import User, Movie, Review, Reply, Genre, FavoriteMovie, Profile, Watchlist, Series, Animation
from django.db.models import Q, Avg
from .forms import UserRegistrationForm, ProfileUpdateForm, ReviewForm, ReplyForm
from .models import Subscription, DownloadLink
from .forms import SubscriptionForm 

# ========================
# ثبت‌نام کاربر
# ========================
def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            login(request, user) 
            messages.success(request, "Registration successful. Welcome!")
            return redirect('home') 
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
            return redirect('home')
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
            return redirect('home') 
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
    messages.success(request, "You have logged out successfully!")
    return redirect('home')


# ========================
# صفحه اصلی
# ========================
def home(request):
    new_movies = Movie.objects.all().order_by('-release_date')[:5]
    new_series = Series.objects.order_by('-release_date')[:4]
    new_animations = Animation.objects.order_by('-release_date')[:4]
    popular_movies = Movie.objects.all().order_by('-view_count')[:5]
    return render(request, 'main/home.html', {
        'new_movies': new_movies,
        'new_series': new_series,
        'new_animations': new_animations,
        'popular_movies': popular_movies,
    })


# ========================
# جزئیات هر فیلم
# ========================
def movie_detail(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    reviews = Review.objects.filter(movie=movie, parent__isnull=True)
    replies = Reply.objects.filter(review__in=reviews)
    download_links = DownloadLink.objects.filter(movie=movie)

    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = movie.favorites.filter(id=request.user.id).exists()

    # افزایش تعداد بازدیدها
    movie.view_count += 1
    movie.save()
    
    if request.method == 'POST':
        # ارسال نقد جدید
        if 'review' in request.POST:
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.movie = movie
                review.user = request.user
                parent_id = request.POST.get('parent_id')  # دریافت parent_id برای پاسخ
                if parent_id:
                    try:
                        parent_review = Review.objects.get(id=parent_id)
                        review.parent = parent_review
                    except Review.DoesNotExist:
                        pass
                review.save()
                return redirect('movie_detail', pk=pk)
        
        # ارسال پاسخ به نقد
        elif 'reply' in request.POST:
            reply_form = ReplyForm(request.POST)
            review_id = request.POST.get('review_id')  # دریافت review_id برای پاسخ
            review = get_object_or_404(Review, id=review_id)
            if reply_form.is_valid():
                reply = reply_form.save(commit=False)
                reply.user = request.user
                reply.review = review
                reply.save()
                return redirect('movie_detail', pk=pk)
        
    else:
        form = ReviewForm()
        reply_form = ReplyForm()

    return render(request, 'main/movie_detail.html', {
        'movie': movie,
        'reviews': reviews,
        'replies': replies,
        'form': form,
        'reply_form': reply_form,
        'is_favorite': is_favorite,
        'genres': movie.genres.all(), 
        'download_links': download_links,
    })

# ========================
# جزئیات هر سریال
# ========================
def series_detail(request, pk):
    series = get_object_or_404(Series, pk=pk)
    reviews = Review.objects.filter(series=series, parent__isnull=True)
    replies = Reply.objects.filter(review__in=reviews)
    download_links = DownloadLink.objects.filter(series=series)

    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = series.favorites.filter(id=request.user.id).exists()

    # افزایش تعداد بازدیدها
    series.view_count += 1
    series.save()

    if request.method == 'POST':
        # ارسال نقد جدید
        if 'review' in request.POST:
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.series = series
                review.user = request.user
                parent_id = request.POST.get('parent_id')  # دریافت parent_id برای پاسخ
                if parent_id:
                    try:
                        parent_review = Review.objects.get(id=parent_id)
                        review.parent = parent_review
                    except Review.DoesNotExist:
                        pass
                review.save()
                return redirect('series_detail', pk=pk)

        # ارسال پاسخ به نقد
        elif 'reply' in request.POST:
            reply_form = ReplyForm(request.POST)
            review_id = request.POST.get('review_id')  # دریافت review_id برای پاسخ
            review = get_object_or_404(Review, id=review_id)
            if reply_form.is_valid():
                reply = reply_form.save(commit=False)
                reply.user = request.user
                reply.review = review
                reply.save()
                return redirect('series_detail', pk=pk)

    else:
        form = ReviewForm()
        reply_form = ReplyForm()

    return render(request, 'main/series_detail.html', {
        'series': series,
        'reviews': reviews,
        'replies': replies,
        'form': form,
        'reply_form': reply_form,
        'is_favorite': is_favorite,
        'genres': series.genres.all(),
        'download_links': download_links,
    })


# ========================
# جزئیات هر انیمیشن
# ========================
def animation_detail(request, pk):
    animation = get_object_or_404(Animation, pk=pk)
    reviews = Review.objects.filter(animation=animation, parent__isnull=True)
    replies = Reply.objects.filter(review__in=reviews)
    download_links = DownloadLink.objects.filter(animation=animation)

    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = animation.favorites.filter(id=request.user.id).exists()

    # افزایش تعداد بازدیدها
    animation.view_count += 1
    animation.save()

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.animation = animation
            review.user = request.user
            parent_id = request.POST.get('parent_id') 
            if parent_id:
                try:
                    parent_review = Review.objects.get(id=parent_id)
                    review.parent = parent_review
                except Review.DoesNotExist:
                    pass
            review.save()
            return redirect('animation_detail', pk=pk)
    else:
        form = ReviewForm()

    return render(request, 'main/animation_detail.html', {
        'animation': animation,
        'reviews': reviews,
        'replies': replies,
        'form': form,
        'is_favorite': is_favorite,
        'download_links': download_links,
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
def search(request):
    query = request.GET.get('q', '')
    movies = Movie.objects.filter(Q(title__icontains=query)) if query else []
    return render(request, 'main/search_results.html', {'movies': movies, 'query': query})


# ========================
# جستجوی پیشرفته
# ========================
def movie_advanced_search(request):
    query = request.GET.get('query', '')
    genre_id = request.GET.get('genre', '')
    rating_filter = request.GET.get('rating', '')
    sort_by = request.GET.get('sort_by', '')

    movies = Movie.objects.all()

    if query:
        movies = movies.filter(Q(title__icontains=query) | Q(description__icontains=query))

    if genre_id:
        movies = movies.filter(genres__id=genre_id)

    if rating_filter:
        if rating_filter == '4':
            movies = movies.filter(overall_rating__lt=5)
        else:
            movies = movies.filter(overall_rating__gte=rating_filter)

    if sort_by == 'newest':
        movies = movies.order_by('-release_date')
    elif sort_by == 'popular':
        movies = movies.order_by('-view_count')
    elif sort_by == 'release_year':
        movies = movies.order_by('-release_date__year')

    genres = Genre.objects.all()

    context = {
        'movies': movies,
        'query': query,
        'genres': genres,
    }
    return render(request, 'main/movie_list.html', context)


def series_advanced_search(request):
    query = request.GET.get('query', '')
    genre_id = request.GET.get('genre', '')
    rating_filter = request.GET.get('rating', '')
    sort_by = request.GET.get('sort_by', '')

    series = Series.objects.all()

    if query:
        series = series.filter(Q(title__icontains=query) | Q(description__icontains=query))

    if genre_id:
        series = series.filter(genres__id=genre_id)

    if rating_filter:
        if rating_filter == '4':
            series = series.filter(overall_rating__lt=5)
        else:
            series = series.filter(overall_rating__gte=rating_filter)

    if sort_by == 'newest':
        series = series.order_by('-start_year')
    elif sort_by == 'popular':
        series = series.order_by('-view_count')
    elif sort_by == 'release_year':
        series = series.order_by('-start_year')

    genres = Genre.objects.all()

    context = {
        'series': series,
        'query': query,
        'genres': genres,
    }
    return render(request, 'main/series_list.html', context)


def animation_advanced_search(request):
    query = request.GET.get('query', '')
    genre_id = request.GET.get('genre', '')
    rating_filter = request.GET.get('rating', '')
    sort_by = request.GET.get('sort_by', '')

    animations = Animation.objects.all()

    if query:
        animations = animations.filter(Q(title__icontains=query) | Q(description__icontains=query))

    if genre_id:
        animations = animations.filter(genres__id=genre_id)

    if rating_filter:
        if rating_filter == '4':
            animations = animations.filter(overall_rating__lt=5)
        else:
            animations = animations.filter(overall_rating__gte=rating_filter)

    if sort_by == 'newest':
        animations = animations.order_by('-release_date')
    elif sort_by == 'popular':
        animations = animations.order_by('-view_count')
    elif sort_by == 'release_year':
        animations = animations.order_by('-release_date')

    genres = Genre.objects.all()

    context = {
        'animations': animations,
        'query': query,
        'genres': genres,
    }
    return render(request, 'main/animation_list.html', context)


# ========================
# نمایش فیلم‌ها بر اساس ژانر
# ========================
def movies_by_genre(request, genre_id):
    genre = get_object_or_404(Genre, pk=genre_id)
    movies = genre.movies.all()
    return render(request, 'main/movies_by_genre.html', {'genre': genre, 'movies': movies})


# ========================
# لیست همه فیلم‌ها
# ========================
def movie_list(request):
    movies = Movie.objects.all() 
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


def series_list(request):
    series = Series.objects.all()
    return render(request, 'main/series_list.html', {'series': series})

def series_detail(request, pk):
    series = get_object_or_404(Series, pk=pk)
    return render(request, 'main/series_detail.html', {'series': series})


def animation_list(request):
    animations = Animation.objects.all()
    return render(request, 'main/animation_list.html', {'animations': animations})


def top_movies(request):
    # محبوب‌ترین فیلم‌ها براساس تعداد بازدید یا امتیاز
    top_movies = Movie.objects.order_by('-rating')[:10] 
    return render(request, 'main/top_movies.html', {'top_movies': top_movies})


def top_series(request):
    # محبوب‌ترین سریالها براساس تعداد بازدید یا امتیاز
    top_series = Series.objects.order_by('-rating')[:10]
    return render(request, 'main/top_series.html', {'top_series': top_series})


def add_to_watchlist(request, movie_id):
    if request.user.is_authenticated:
        movie = get_object_or_404(Movie, id=movie_id)
        watchlist_item, created = Watchlist.objects.get_or_create(user=request.user, movie=movie)
        if created:
            message = f"{movie.title} was added to your watchlist."
        else:
            message = f"{movie.title} is already in your watchlist."
    else:
        message = "You need to log in to manage your watchlist."
    return redirect('watchlist')


def remove_from_watchlist(request, movie_id):
    if request.user.is_authenticated:
        movie = get_object_or_404(Movie, id=movie_id)
        Watchlist.objects.filter(user=request.user, movie=movie).delete()
        message = f"{movie.title} was removed from your watchlist."
    else:
        message = "You need to log in to manage your watchlist."
    return redirect('watchlist')


def watchlist_view(request):
    if request.user.is_authenticated:
        watchlist = Watchlist.objects.filter(user=request.user).select_related('movie')
    else:
        watchlist = []
    return render(request, 'main/watchlist.html', {'watchlist': watchlist})


@login_required
def subscription(request):
    try:
        subscription = Subscription.objects.get(user=request.user)
    except Subscription.DoesNotExist:
        subscription = None

    return render(request, 'main/subscription.html', {'subscription': subscription})

@login_required
def update_subscription(request):
    if request.method == 'POST':
        subscription = Subscription.objects.get(user=request.user)
        subscription.subscription_type = request.POST.get('subscription_type')
        subscription.end_date = request.POST.get('end_date')
        subscription.save()
        return redirect('subscription')  # به صفحه نمایش اشتراک‌ها بروید

    return render(request, 'main/update_subscription.html')  # صفحه ویرایش اشتراک
