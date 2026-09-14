from datetime import date

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .exceptions import DomainError
from .forms import (
    ProfileUpdateForm,
    ReplyForm,
    ReviewForm,
    SubscriptionForm,
    UserRegistrationForm,
)
from .models import Animation, DownloadLink, Genre, Movie, Profile, Review, Series
from .permissions import is_staff_user, staff_required
from .services import (
    AlertService,
    EntitlementService,
    FavoriteService,
    RecommendationService,
    ReviewService,
    SearchService,
    SubscriptionService,
    ViewCountService,
    WatchlistService,
)

CATALOG_PAGE_SIZE = 12


def _paginate(request, queryset, per_page=CATALOG_PAGE_SIZE):
    paginator = Paginator(queryset, per_page)
    page_obj = paginator.get_page(request.GET.get('page'))
    query = request.GET.copy()
    query.pop('page', None)
    return page_obj, query.urlencode()


def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.email = form.cleaned_data['email']
            user.save()
            login(request, user)
            messages.success(request, 'Registration successful. Welcome!')
            return redirect('home')
        messages.error(request, 'Please fix the errors below and try again.')
    else:
        form = UserRegistrationForm()
    return render(request, 'main/register.html', {'form': form})


@login_required
def profile_view(request):
    Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'main/profile.html', {'form': form})


def home(request):
    return render(
        request,
        'main/home.html',
        {
            'new_movies': Movie.objects.order_by('-release_date')[:5],
            'new_series': Series.objects.order_by('-release_date')[:4],
            'new_animations': Animation.objects.order_by('-release_date')[:4],
            'popular_movies': Movie.objects.order_by('-view_count')[:5],
            'recommended_movies': RecommendationService.recommend_movies(request.user, limit=5),
        },
    )


def _handle_review_post(request, *, movie=None, series=None, animation=None, redirect_name=None, pk=None):
    form = ReviewForm()
    reply_form = ReplyForm()

    if request.method != 'POST':
        return form, reply_form, False

    if not request.user.is_authenticated:
        messages.error(request, 'You need to log in to post a review.')
        return form, reply_form, redirect('login')

    try:
        if 'review' in request.POST:
            form = ReviewForm(request.POST)
            if form.is_valid():
                ReviewService.create_review(
                    user=request.user,
                    rating=form.cleaned_data['rating'],
                    review_text=form.cleaned_data.get('review_text'),
                    movie=movie,
                    series=series,
                    animation=animation,
                    parent_id=request.POST.get('parent_id'),
                )
                messages.success(request, 'Review posted.')
                return form, reply_form, redirect(redirect_name, pk=pk)
        elif 'reply' in request.POST:
            reply_form = ReplyForm(request.POST)
            parent_filters = {'id': request.POST.get('review_id')}
            if movie is not None:
                parent_filters['movie'] = movie
            elif series is not None:
                parent_filters['series'] = series
            else:
                parent_filters['animation'] = animation
            parent = get_object_or_404(Review, **parent_filters)
            if reply_form.is_valid():
                ReviewService.create_reply(
                    user=request.user,
                    parent_review=parent,
                    reply_text=reply_form.cleaned_data['reply_text'],
                )
                messages.success(request, 'Reply posted.')
                return form, reply_form, redirect(redirect_name, pk=pk)
    except DomainError as exc:
        messages.error(request, exc.message)

    return form, reply_form, False


def movie_detail(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    form, reply_form, early = _handle_review_post(
        request, movie=movie, redirect_name='movie_detail', pk=pk
    )
    if early:
        return early

    if request.method != 'POST':
        ViewCountService.bump(Movie, pk)
        movie.refresh_from_db(fields=['view_count'])

    return render(
        request,
        'main/movie_detail.html',
        {
            'movie': movie,
            'reviews': Review.objects.filter(movie=movie, parent__isnull=True),
            'form': form,
            'reply_form': reply_form,
            'is_favorite': FavoriteService.is_favorite_movie(request.user, movie),
            'is_watchlisted': WatchlistService.is_watchlist_movie(request.user, movie),
            'genres': movie.genres.all(),
            'download_links': DownloadLink.objects.filter(movie=movie),
            'can_download': EntitlementService.can_download(request.user),
        },
    )


def series_detail(request, pk):
    series = get_object_or_404(Series, pk=pk)
    form, reply_form, early = _handle_review_post(
        request, series=series, redirect_name='series_detail', pk=pk
    )
    if early:
        return early

    if request.method != 'POST':
        ViewCountService.bump(Series, pk)
        series.refresh_from_db(fields=['view_count'])

    return render(
        request,
        'main/series_detail.html',
        {
            'series': series,
            'reviews': Review.objects.filter(series=series, parent__isnull=True),
            'form': form,
            'reply_form': reply_form,
            'is_favorite': FavoriteService.is_favorite_series(request.user, series),
            'is_watchlisted': WatchlistService.is_watchlist_series(request.user, series),
            'genres': series.genres.all(),
            'download_links': DownloadLink.objects.filter(series=series),
            'can_download': EntitlementService.can_download(request.user),
        },
    )


def animation_detail(request, pk):
    animation = get_object_or_404(Animation, pk=pk)
    form, reply_form, early = _handle_review_post(
        request, animation=animation, redirect_name='animation_detail', pk=pk
    )
    if early:
        return early

    if request.method != 'POST':
        ViewCountService.bump(Animation, pk)
        animation.refresh_from_db(fields=['view_count'])

    return render(
        request,
        'main/animation_detail.html',
        {
            'animation': animation,
            'reviews': Review.objects.filter(animation=animation, parent__isnull=True),
            'form': form,
            'reply_form': reply_form,
            'is_favorite': FavoriteService.is_favorite_animation(request.user, animation),
            'is_watchlisted': WatchlistService.is_watchlist_animation(request.user, animation),
            'genres': animation.genres.all(),
            'download_links': DownloadLink.objects.filter(animation=animation),
            'can_download': EntitlementService.can_download(request.user),
        },
    )


def _resolve_catalog_target(kind: str, pk: int):
    kind = (kind or '').lower()
    if kind == 'movie':
        return {'movie': get_object_or_404(Movie, pk=pk)}
    if kind == 'series':
        return {'series': get_object_or_404(Series, pk=pk)}
    if kind == 'animation':
        return {'animation': get_object_or_404(Animation, pk=pk)}
    raise Http404('Unknown catalog kind.')


def _catalog_redirect(kind: str, pk: int):
    if kind == 'movie':
        return redirect('movie_detail', pk=pk)
    if kind == 'series':
        return redirect('series_detail', pk=pk)
    return redirect('animation_detail', pk=pk)


@login_required
@require_POST
def add_to_favorites(request, kind, pk):
    target = _resolve_catalog_target(kind, pk)
    try:
        FavoriteService.add_item(request.user, **target)
        title = next(iter(target.values())).title
        messages.success(request, f'{title} was added to your favorites.')
    except DomainError as exc:
        messages.error(request, exc.message)
    return _catalog_redirect(kind, pk)


@login_required
@require_POST
def remove_from_favorites(request, kind, pk):
    target = _resolve_catalog_target(kind, pk)
    try:
        FavoriteService.remove_item(request.user, **target)
        title = next(iter(target.values())).title
        messages.success(request, f'{title} was removed from your favorites.')
    except DomainError as exc:
        messages.error(request, exc.message)
    return redirect('favorites_list')


@login_required
def favorites_list(request):
    favorites = FavoriteService.list_for(request.user)
    return render(request, 'main/favorites_list.html', {'favorites': favorites})


@login_required
def download_unlock(request, pk):
    """Server-side unlock — never embed raw CDN URLs in templates for gated downloads."""
    try:
        EntitlementService.assert_can_download(request.user)
    except DomainError as exc:
        messages.error(request, exc.message)
        return redirect('subscription')
    link = get_object_or_404(DownloadLink, pk=pk)
    return redirect(link.download_url)


def search(request):
    query = request.GET.get('q', '').strip()
    results = SearchService.search_all(query) if query else []
    return render(request, 'main/search_results.html', {'results': results, 'query': query})


@login_required
def notifications_list(request):
    items = AlertService.recent_for(request.user, limit=40)
    return render(request, 'main/notifications.html', {'notifications': items})


@login_required
@require_POST
def notification_mark_read(request, pk):
    AlertService.mark_read(request.user, pk)
    return redirect('notifications_list')


def _apply_rating_filter(queryset, rating_filter):
    if not rating_filter:
        return queryset
    try:
        value = float(rating_filter)
    except (TypeError, ValueError):
        return queryset
    if rating_filter == '4':
        return queryset.filter(overall_rating__lt=5)
    return queryset.filter(overall_rating__gte=value)


def movie_advanced_search(request):
    query = request.GET.get('query', '')
    genre_id = request.GET.get('genre', '')
    rating_filter = request.GET.get('rating', '')
    sort_by = request.GET.get('sort_by', '')

    movies = Movie.objects.all().order_by('-release_date', 'title')
    if query:
        movies = movies.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if genre_id:
        movies = movies.filter(genres__id=genre_id)
    movies = _apply_rating_filter(movies, rating_filter)

    if sort_by == 'newest':
        movies = movies.order_by('-release_date')
    elif sort_by == 'popular':
        movies = movies.order_by('-view_count')
    elif sort_by == 'release_year':
        movies = movies.order_by('-release_date')

    page_obj, querystring = _paginate(request, movies.distinct().order_by('-release_date', 'title'))
    return render(
        request,
        'main/movie_list.html',
        {
            'movies': page_obj,
            'page_obj': page_obj,
            'querystring': querystring,
            'query': query,
            'genres': Genre.objects.all(),
        },
    )


def series_advanced_search(request):
    query = request.GET.get('query', '')
    genre_id = request.GET.get('genre', '')
    rating_filter = request.GET.get('rating', '')
    sort_by = request.GET.get('sort_by', '')

    series = Series.objects.all().order_by('-release_date', 'title')
    if query:
        series = series.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if genre_id:
        series = series.filter(genres__id=genre_id)
    series = _apply_rating_filter(series, rating_filter)

    if sort_by == 'newest':
        series = series.order_by('-start_year')
    elif sort_by == 'popular':
        series = series.order_by('-view_count')
    elif sort_by == 'release_year':
        series = series.order_by('-start_year')

    page_obj, querystring = _paginate(request, series.distinct().order_by('-release_date', 'title'))
    return render(
        request,
        'main/series_list.html',
        {
            'series': page_obj,
            'page_obj': page_obj,
            'querystring': querystring,
            'query': query,
            'genres': Genre.objects.all(),
        },
    )


def animation_advanced_search(request):
    query = request.GET.get('query', '')
    genre_id = request.GET.get('genre', '')
    rating_filter = request.GET.get('rating', '')
    sort_by = request.GET.get('sort_by', '')

    animations = Animation.objects.all().order_by('-release_date', 'title')
    if query:
        animations = animations.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    if genre_id:
        animations = animations.filter(genres__id=genre_id)
    animations = _apply_rating_filter(animations, rating_filter)

    if sort_by in ('newest', 'release_year'):
        animations = animations.order_by('-release_date')
    elif sort_by == 'popular':
        animations = animations.order_by('-view_count')

    page_obj, querystring = _paginate(request, animations.distinct().order_by('-release_date', 'title'))
    return render(
        request,
        'main/animation_list.html',
        {
            'animations': page_obj,
            'page_obj': page_obj,
            'querystring': querystring,
            'query': query,
            'genres': Genre.objects.all(),
        },
    )


def movies_by_genre(request, genre_id):
    genre = get_object_or_404(Genre, pk=genre_id)
    page_obj, querystring = _paginate(request, genre.movies.order_by('-release_date', 'title'))
    return render(
        request,
        'main/movies_by_genre.html',
        {
            'genre': genre,
            'movies': page_obj,
            'page_obj': page_obj,
            'querystring': querystring,
        },
    )


def movie_list(request):
    page_obj, querystring = _paginate(request, Movie.objects.order_by('-release_date', 'title'))
    return render(
        request,
        'main/movie_list.html',
        {
            'movies': page_obj,
            'page_obj': page_obj,
            'querystring': querystring,
            'genres': Genre.objects.all(),
        },
    )


def series_list(request):
    page_obj, querystring = _paginate(request, Series.objects.order_by('-release_date', 'title'))
    return render(
        request,
        'main/series_list.html',
        {
            'series': page_obj,
            'page_obj': page_obj,
            'querystring': querystring,
            'genres': Genre.objects.all(),
        },
    )


def animation_list(request):
    page_obj, querystring = _paginate(request, Animation.objects.order_by('-release_date', 'title'))
    return render(
        request,
        'main/animation_list.html',
        {
            'animations': page_obj,
            'page_obj': page_obj,
            'querystring': querystring,
            'genres': Genre.objects.all(),
        },
    )


def filter_movies(request):
    genre = request.GET.get('genre')
    language = request.GET.get('language')
    min_rating = request.GET.get('min_rating')

    movies = Movie.objects.all().order_by('-release_date', 'title')
    if genre:
        movies = movies.filter(genres__genre_name__iexact=genre)
    if language:
        movies = movies.filter(language__iexact=language)
    if min_rating:
        try:
            movies = movies.annotate(avg_rating=Avg('reviews__rating')).filter(
                avg_rating__gte=float(min_rating)
            )
        except (TypeError, ValueError):
            pass

    page_obj, querystring = _paginate(request, movies.distinct().order_by('-release_date', 'title'))
    return render(
        request,
        'main/filter_movies.html',
        {
            'movies': page_obj,
            'page_obj': page_obj,
            'querystring': querystring,
            'genres': Genre.objects.all(),
            'selected_genre': genre,
            'selected_language': language,
            'selected_min_rating': min_rating,
        },
    )


def genre_list(request):
    return render(request, 'main/genre_list.html', {'genres': Genre.objects.all()})


def top_movies(request):
    return render(
        request,
        'main/top_movies.html',
        {'top_movies': Movie.objects.order_by('-overall_rating', '-view_count')[:10]},
    )


def top_series(request):
    return render(
        request,
        'main/top_series.html',
        {'top_series': Series.objects.order_by('-overall_rating', '-view_count')[:10]},
    )


@login_required
@require_POST
def add_to_watchlist(request, kind, pk):
    target = _resolve_catalog_target(kind, pk)
    try:
        _, created = WatchlistService.add_item(request.user, **target)
        title = next(iter(target.values())).title
        if created:
            messages.success(request, f'{title} was added to your watchlist.')
        else:
            messages.info(request, f'{title} is already in your watchlist.')
    except DomainError as exc:
        messages.error(request, exc.message)
    return _catalog_redirect(kind, pk)


@login_required
@require_POST
def remove_from_watchlist(request, kind, pk):
    target = _resolve_catalog_target(kind, pk)
    try:
        WatchlistService.remove_item(request.user, **target)
        title = next(iter(target.values())).title
        messages.success(request, f'{title} was removed from your watchlist.')
    except DomainError as exc:
        messages.error(request, exc.message)
    return redirect('watchlist')


@login_required
def watchlist_view(request):
    return render(
        request,
        'main/watchlist.html',
        {'watchlist': WatchlistService.list_for(request.user)},
    )


@login_required
def subscription(request):
    subscription_obj = SubscriptionService.current_for(request.user)
    return render(
        request,
        'main/subscription.html',
        {
            'subscription': subscription_obj,
            'has_premium_access': request.user.has_premium_access(),
            'is_staff': is_staff_user(request.user),
            'user_role': request.user.role,
        },
    )


@login_required
@require_POST
def request_premium_upgrade(request):
    try:
        SubscriptionService.request_upgrade(
            user=request.user, note=request.POST.get('note', '')
        )
        messages.success(
            request,
            'Upgrade request recorded. A staff member must activate Premium.',
        )
    except DomainError as exc:
        messages.error(request, exc.message)
    return redirect('subscription')


@staff_required
def update_subscription(request):
    """Staff-only subscription assignment (no free self-upgrade)."""
    from django.contrib.auth import get_user_model

    User = get_user_model()
    target = request.user
    user_id = request.GET.get('user') or request.POST.get('user')
    if user_id:
        target = get_object_or_404(User, pk=user_id)

    subscription_obj = SubscriptionService.current_for(target)

    if request.method == 'POST':
        form = SubscriptionForm(request.POST, instance=subscription_obj)
        if form.is_valid():
            try:
                SubscriptionService.assign(
                    user=target,
                    actor=request.user,
                    subscription_type=form.cleaned_data['subscription_type'],
                    end_date=form.cleaned_data['end_date'],
                    start_date=date.today(),
                    reason='staff_form',
                )
                messages.success(request, f'Subscription updated for {target.username}.')
                return redirect('subscription')
            except DomainError as exc:
                messages.error(request, exc.message)
    else:
        form = SubscriptionForm(instance=subscription_obj)

    return render(
        request,
        'main/update_subscription.html',
        {'form': form, 'target_user': target},
    )


@staff_required
@require_POST
def mock_checkout(request):
    """Staff-only demo premium grant for thesis/demo flows."""
    days = int(request.POST.get('days', 30))
    try:
        SubscriptionService.grant_demo_premium_days(
            user=request.user, actor=request.user, days=days
        )
        messages.success(request, f'Demo premium granted for {days} days.')
    except DomainError as exc:
        messages.error(request, exc.message)
    return redirect('subscription')


def spa_browse(request):
    """Optional JWT browse client (portfolio). Main product remains SSR templates."""
    return render(request, 'spa/browse.html')
