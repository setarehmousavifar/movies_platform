from datetime import date

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, UniqueConstraint, CheckConstraint, F, Index


class User(AbstractUser):
    """Custom user. Premium access is derived from Subscription; is_premium is a cache flag."""

    is_premium = models.BooleanField(default=False, verbose_name='وضعیت پریمیوم')
    profile_picture = models.ImageField(
        upload_to='profile_pictures/', null=True, blank=True, verbose_name='عکس پروفایل'
    )
    wallet_balance = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0, verbose_name='موجودی کیف پول'
    )
    registration_date = models.DateField(auto_now_add=True, verbose_name='تاریخ ثبت‌نام')
    phone_number = models.CharField(max_length=15, null=True, blank=True, verbose_name='شماره تلفن')

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        constraints = [
            UniqueConstraint(
                fields=['email'],
                condition=~Q(email=''),
                name='unique_nonempty_user_email',
            ),
        ]

    def __str__(self):
        return self.username

    def has_premium_access(self):
        today = date.today()
        return self.subscriptions.filter(
            is_active=True,
            subscription_type='premium',
            start_date__lte=today,
            end_date__gte=today,
        ).exists()

    def sync_premium_flag(self):
        desired = self.has_premium_access()
        if self.is_premium != desired:
            self.is_premium = desired
            self.save(update_fields=['is_premium'])
        return desired

    @property
    def role(self):
        from main.permissions import role_of

        return role_of(self)


class AgeRating(models.Model):
    RATINGS = [
        ('G', 'General Audiences (همه سنین)'),
        ('PG', 'Parental Guidance (مشورت والدین)'),
        ('PG-13', 'Parents Strongly Cautioned (13+ با مشورت)'),
        ('R', 'Restricted (17+ با محدودیت)'),
        ('NC-17', 'No Children Under 17 (غیرقابل مشاهده برای زیر 17)'),
    ]

    name = models.CharField(
        max_length=50, choices=RATINGS, unique=True, verbose_name='رده‌بندی سنی', default='G'
    )
    description = models.TextField(null=True, blank=True, verbose_name='توضیحات')

    def __str__(self):
        return self.get_name_display()


class CatalogItem(models.Model):
    """Shared catalog fields for Movie / Series / Animation (abstract — no DB table)."""

    title = models.CharField(max_length=200, verbose_name='عنوان')
    release_date = models.DateField(verbose_name='تاریخ انتشار')
    description = models.TextField(verbose_name='توضیحات')
    duration = models.PositiveIntegerField(verbose_name='مدت زمان (دقیقه)')
    view_count = models.PositiveIntegerField(default=0, db_index=True, verbose_name='تعداد بازدید')
    poster_url = models.URLField(null=True, blank=True, verbose_name='پوستر (لینک)')
    poster_image = models.ImageField(
        upload_to='posters/', null=True, blank=True, verbose_name='پوستر (تصویر)'
    )
    background_poster = models.ImageField(
        upload_to='backgrounds/', null=True, blank=True, verbose_name='پوستر پس‌زمینه'
    )
    language = models.CharField(max_length=50, db_index=True, verbose_name='زبان')
    age_rating = models.ForeignKey(
        AgeRating, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='رده‌بندی سنی'
    )
    overall_rating = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.0, db_index=True, verbose_name='امتیاز کلی'
    )
    country = models.CharField(max_length=100, verbose_name='کشور تولید')
    trailer_url = models.URLField(null=True, blank=True, verbose_name='لینک تریلر')
    trailer_video = models.FileField(
        upload_to='trailers/', null=True, blank=True, verbose_name='ویدئو تریلر'
    )
    ai_summary = models.TextField(blank=True, default='', verbose_name='خلاصه هوشمند')
    ai_tags = models.JSONField(default=list, blank=True, verbose_name='برچسب‌های هوشمند')
    ai_enriched_at = models.DateTimeField(null=True, blank=True, verbose_name='زمان غنی‌سازی AI')

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    def get_poster(self):
        if self.poster_image:
            return self.poster_image.url
        if self.poster_url:
            return self.poster_url
        return None

    def get_duration(self):
        hours = self.duration // 60
        minutes = self.duration % 60
        return f'{hours}h {minutes}m' if hours > 0 else f'{minutes}m'


class Genre(models.Model):
    genre_name = models.CharField(max_length=100, unique=True, verbose_name='نام ژانر')
    description = models.TextField(null=True, blank=True, verbose_name='توضیحات')

    def __str__(self):
        return self.genre_name


class Actor(models.Model):
    name = models.CharField(max_length=100, verbose_name='نام بازیگر')
    birth_date = models.DateField(verbose_name='تاریخ تولد')
    nationality = models.CharField(max_length=50, verbose_name='ملیت')

    def __str__(self):
        return self.name


class Director(models.Model):
    name = models.CharField(max_length=100, verbose_name='نام کارگردان')
    birth_date = models.DateField(verbose_name='تاریخ تولد')
    nationality = models.CharField(max_length=50, verbose_name='ملیت')

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='نام برچسب')
    description = models.TextField(null=True, blank=True, verbose_name='توضیحات')

    def __str__(self):
        return self.name


class Movie(CatalogItem):
    genres = models.ManyToManyField(Genre, related_name='movies', verbose_name='ژانرها')
    directors = models.ManyToManyField(Director, related_name='movies', verbose_name='کارگردان‌ها')
    stars = models.ManyToManyField(Actor, related_name='movies', verbose_name='بازیگران')
    tags = models.ManyToManyField(Tag, blank=True, verbose_name='برچسب‌ها')

    class Meta:
        indexes = [
            Index(fields=['title']),
            Index(fields=['-release_date']),
            Index(fields=['-view_count']),
            Index(fields=['-overall_rating']),
        ]


class Series(CatalogItem):
    start_year = models.PositiveIntegerField(verbose_name='سال شروع')
    end_year = models.PositiveIntegerField(null=True, blank=True, verbose_name='سال پایان')
    status = models.CharField(
        max_length=20,
        choices=[('ongoing', 'در حال پخش'), ('ended', 'تمام شده')],
        verbose_name='وضعیت پخش',
    )
    # Denormalized counts; prefer season_list / episode counts via related models when present.
    season_count = models.PositiveIntegerField(default=0, verbose_name='تعداد فصل‌ها')
    episode_count = models.PositiveIntegerField(default=0, verbose_name='تعداد قسمت‌ها')
    genres = models.ManyToManyField(Genre, related_name='series', verbose_name='ژانرها')
    directors = models.ManyToManyField(Director, related_name='series', verbose_name='کارگردان‌ها')
    stars = models.ManyToManyField(Actor, related_name='series', verbose_name='بازیگران')
    tags = models.ManyToManyField(Tag, blank=True, verbose_name='برچسب‌ها')

    class Meta:
        verbose_name_plural = 'Series'
        indexes = [
            Index(fields=['title']),
            Index(fields=['-release_date']),
            Index(fields=['-view_count']),
            Index(fields=['-overall_rating']),
            Index(fields=['-start_year']),
        ]
        constraints = [
            CheckConstraint(
                condition=Q(end_year__isnull=True) | Q(end_year__gte=F('start_year')),
                name='series_end_year_gte_start_year',
            ),
        ]

    def get_years(self):
        return f"{self.start_year}–{self.end_year if self.end_year else ''}"

    def refresh_episode_counts(self):
        seasons = self.season_list.count()
        episodes = Episode.objects.filter(season__series=self).count()
        self.season_count = seasons
        self.episode_count = episodes
        self.save(update_fields=['season_count', 'episode_count'])


class Animation(CatalogItem):
    genres = models.ManyToManyField(Genre, related_name='animations', verbose_name='ژانرها')
    tags = models.ManyToManyField(Tag, blank=True, verbose_name='برچسب‌ها')
    directors = models.ManyToManyField(
        Director, related_name='animations', blank=True, verbose_name='کارگردان‌ها'
    )
    stars = models.ManyToManyField(
        Actor, related_name='animations', blank=True, verbose_name='بازیگران'
    )

    class Meta:
        indexes = [
            Index(fields=['title']),
            Index(fields=['-release_date']),
            Index(fields=['-view_count']),
            Index(fields=['-overall_rating']),
        ]


def _exactly_one_target(movie_id, series_id, animation_id):
    return sum(x is not None for x in (movie_id, series_id, animation_id)) == 1


class Season(models.Model):
    series = models.ForeignKey(
        Series,
        on_delete=models.CASCADE,
        related_name='season_list',
        verbose_name='سریال',
        null=True,
        blank=True,
    )
    season_number = models.PositiveIntegerField(verbose_name='شماره فصل')
    description = models.TextField(null=True, blank=True, verbose_name='توضیحات')

    class Meta:
        ordering = ['season_number']
        constraints = [
            UniqueConstraint(fields=['series', 'season_number'], name='unique_series_season_number'),
        ]

    def __str__(self):
        return f'{self.series.title} - فصل {self.season_number}'


class Episode(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='episodes', verbose_name='فصل')
    episode_number = models.PositiveIntegerField(verbose_name='شماره قسمت')
    title = models.CharField(max_length=200, verbose_name='عنوان قسمت')
    duration = models.PositiveIntegerField(verbose_name='مدت زمان (دقیقه)')

    class Meta:
        ordering = ['episode_number']
        constraints = [
            UniqueConstraint(
                fields=['season', 'episode_number'], name='unique_season_episode_number'
            ),
        ]

    def __str__(self):
        return (
            f'{self.season.series.title} - فصل {self.season.season_number} '
            f'- قسمت {self.episode_number}'
        )


class WalletTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wallet_transactions')
    transaction_type = models.CharField(
        max_length=50, choices=[('credit', 'شارژ'), ('debit', 'برداشت')], verbose_name='نوع تراکنش'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='مبلغ تراکنش')
    transaction_date = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ تراکنش')

    class Meta:
        indexes = [Index(fields=['user', '-transaction_date'])]
        constraints = [
            CheckConstraint(condition=Q(amount__gt=0), name='wallet_amount_positive'),
        ]

    def __str__(self):
        return f'{self.user.username} - {self.transaction_type} - {self.amount}'


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    subscription_type = models.CharField(
        max_length=50, choices=[('basic', 'Basic'), ('premium', 'Premium')], default='basic'
    )
    start_date = models.DateField(verbose_name='تاریخ شروع')
    end_date = models.DateField(verbose_name='تاریخ پایان')
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [Index(fields=['user', 'is_active', '-end_date'])]
        constraints = [
            CheckConstraint(
                condition=Q(end_date__gte=F('start_date')),
                name='subscription_end_gte_start',
            ),
        ]

    def __str__(self):
        return f'{self.user.username} - {self.subscription_type}'

    def is_currently_valid(self):
        today = date.today()
        return self.is_active and self.start_date <= today <= self.end_date

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.user.sync_premium_flag()


class Review(models.Model):
    """Single threading model via parent; replies are child Review rows."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE, null=True, blank=True, related_name='reviews'
    )
    series = models.ForeignKey(
        Series, on_delete=models.CASCADE, null=True, blank=True, related_name='reviews'
    )
    animation = models.ForeignKey(
        Animation, on_delete=models.CASCADE, null=True, blank=True, related_name='reviews'
    )
    rating = models.PositiveIntegerField(verbose_name='امتیاز')
    review_text = models.TextField(null=True, blank=True, verbose_name='متن نقد')
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies'
    )
    review_date = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ نقد')

    class Meta:
        indexes = [
            Index(fields=['movie', 'parent']),
            Index(fields=['series', 'parent']),
            Index(fields=['animation', 'parent']),
            Index(fields=['user', '-review_date']),
        ]
        constraints = [
            CheckConstraint(
                condition=Q(rating__gte=1) & Q(rating__lte=10),
                name='review_rating_range_1_10',
            ),
            CheckConstraint(
                condition=(
                    Q(movie__isnull=False, series__isnull=True, animation__isnull=True)
                    | Q(movie__isnull=True, series__isnull=False, animation__isnull=True)
                    | Q(movie__isnull=True, series__isnull=True, animation__isnull=False)
                ),
                name='review_exactly_one_target',
            ),
        ]

    def clean(self):
        if not _exactly_one_target(self.movie_id, self.series_id, self.animation_id):
            raise ValidationError('Review must target exactly one of movie, series, or animation.')

    def target_title(self):
        if self.movie_id:
            return self.movie.title
        if self.series_id:
            return self.series.title
        if self.animation_id:
            return self.animation.title
        return 'Unknown'

    def __str__(self):
        return f'{self.user.username} - {self.target_title()} - {self.rating}'


class FavoriteItem(models.Model):
    """Unified favorites for movie / series / animation."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_items')
    movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE, null=True, blank=True, related_name='favorited_by_items'
    )
    series = models.ForeignKey(
        Series, on_delete=models.CASCADE, null=True, blank=True, related_name='favorited_by_items'
    )
    animation = models.ForeignKey(
        Animation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='favorited_by_items',
    )
    added_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            CheckConstraint(
                condition=(
                    Q(movie__isnull=False, series__isnull=True, animation__isnull=True)
                    | Q(movie__isnull=True, series__isnull=False, animation__isnull=True)
                    | Q(movie__isnull=True, series__isnull=True, animation__isnull=False)
                ),
                name='favorite_exactly_one_target',
            ),
            UniqueConstraint(
                fields=['user', 'movie'],
                condition=Q(movie__isnull=False),
                name='unique_user_favorite_movie',
            ),
            UniqueConstraint(
                fields=['user', 'series'],
                condition=Q(series__isnull=False),
                name='unique_user_favorite_series',
            ),
            UniqueConstraint(
                fields=['user', 'animation'],
                condition=Q(animation__isnull=False),
                name='unique_user_favorite_animation',
            ),
        ]

    def __str__(self):
        target = self.movie or self.series or self.animation
        return f'{self.user.username} - {target}'


class Watchlist(models.Model):
    """Unified watchlist for movie / series / animation."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist_items')
    movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE, null=True, blank=True, related_name='watchlisted_by'
    )
    series = models.ForeignKey(
        Series, on_delete=models.CASCADE, null=True, blank=True, related_name='watchlisted_by'
    )
    animation = models.ForeignKey(
        Animation, on_delete=models.CASCADE, null=True, blank=True, related_name='watchlisted_by'
    )
    added_date = models.DateTimeField(auto_now_add=True, verbose_name='Date Added')

    class Meta:
        verbose_name = 'Watchlist Item'
        verbose_name_plural = 'Watchlist Items'
        constraints = [
            CheckConstraint(
                condition=(
                    Q(movie__isnull=False, series__isnull=True, animation__isnull=True)
                    | Q(movie__isnull=True, series__isnull=False, animation__isnull=True)
                    | Q(movie__isnull=True, series__isnull=True, animation__isnull=False)
                ),
                name='watchlist_exactly_one_target',
            ),
            UniqueConstraint(
                fields=['user', 'movie'],
                condition=Q(movie__isnull=False),
                name='unique_user_watchlist_movie',
            ),
            UniqueConstraint(
                fields=['user', 'series'],
                condition=Q(series__isnull=False),
                name='unique_user_watchlist_series',
            ),
            UniqueConstraint(
                fields=['user', 'animation'],
                condition=Q(animation__isnull=False),
                name='unique_user_watchlist_animation',
            ),
        ]

    def __str__(self):
        target = self.movie or self.series or self.animation
        return f'{self.user.username} - {target}'


class DownloadLink(models.Model):
    movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE, null=True, blank=True, related_name='download_links'
    )
    series = models.ForeignKey(
        Series, on_delete=models.CASCADE, null=True, blank=True, related_name='download_links'
    )
    animation = models.ForeignKey(
        Animation, on_delete=models.CASCADE, null=True, blank=True, related_name='download_links'
    )
    quality = models.CharField(
        max_length=20, choices=[('720p', '720p'), ('1080p', '1080p'), ('4K', '4K')]
    )
    download_url = models.URLField()
    file_size = models.CharField(max_length=50)

    class Meta:
        constraints = [
            CheckConstraint(
                condition=(
                    Q(movie__isnull=False, series__isnull=True, animation__isnull=True)
                    | Q(movie__isnull=True, series__isnull=False, animation__isnull=True)
                    | Q(movie__isnull=True, series__isnull=True, animation__isnull=False)
                ),
                name='downloadlink_exactly_one_target',
            ),
        ]

    def target_title(self):
        if self.movie_id:
            return self.movie.title
        if self.series_id:
            return self.series.title
        if self.animation_id:
            return self.animation.title
        return 'Unknown'

    def __str__(self):
        return f'{self.target_title()} - {self.quality} ({self.file_size})'


class WatchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watch_history')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, null=True, blank=True)
    series = models.ForeignKey(Series, on_delete=models.CASCADE, null=True, blank=True)
    animation = models.ForeignKey(Animation, on_delete=models.CASCADE, null=True, blank=True)
    watch_datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [Index(fields=['user', '-watch_datetime'])]
        verbose_name_plural = 'Watch histories'

    def __str__(self):
        target = self.movie or self.series or self.animation
        return f'{self.user.username} - {target} - {self.watch_datetime}'


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField(verbose_name='پیام اعلان')
    sent_date = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ارسال')
    is_read = models.BooleanField(default=False, verbose_name='خوانده شده')

    class Meta:
        indexes = [Index(fields=['user', 'is_read', '-sent_date'])]

    def __str__(self):
        return f'{self.user.username} - {self.message[:20]}...'


class Subtitle(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='subtitles')
    language = models.CharField(max_length=50, verbose_name='زبان زیرنویس')
    subtitle_file = models.URLField(verbose_name='فایل زیرنویس')

    def __str__(self):
        return f'{self.movie.title} - {self.language}'


class VideoQuality(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='video_qualities')
    quality = models.CharField(
        max_length=20,
        choices=[('480p', '480p'), ('720p', '720p'), ('1080p', '1080p'), ('2k', '2k'), ('4K', '4K')],
    )
    stream_url = models.URLField(verbose_name='لینک پخش آنلاین')
    download_url = models.URLField(verbose_name='لینک دانلود')

    def __str__(self):
        return f'{self.movie.title} - {self.quality}'


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='likes')
    liked = models.BooleanField(default=True, verbose_name='لایک شده')

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'movie'], name='unique_user_movie_like'),
        ]

    def __str__(self):
        return f'{self.user.username} - {self.movie.title} - {"Liked" if self.liked else "Disliked"}'


class Playlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playlists')
    name = models.CharField(max_length=100, verbose_name='نام لیست پخش')
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.name}'


class PlaylistItem(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, related_name='items')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['playlist', 'movie'], name='unique_playlist_movie'),
        ]

    def __str__(self):
        return f'{self.playlist.name} - {self.movie.title}'


class Recommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    recommended_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'movie'], name='unique_user_recommendation'),
        ]

    def __str__(self):
        return f'{self.user.username} - {self.movie.title}'


class UserGenrePreference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='genre_preferences')
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    preference_level = models.PositiveIntegerField(verbose_name='سطح علاقه (1 تا 5)')

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'genre'], name='unique_user_genre_preference'),
            CheckConstraint(
                condition=Q(preference_level__gte=1) & Q(preference_level__lte=5),
                name='preference_level_1_5',
            ),
        ]

    def __str__(self):
        return f'{self.user.username} - {self.genre.genre_name} - interest {self.preference_level}'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Category Name')
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class AuditLog(models.Model):
    """Immutable-ish audit trail for billing/role-sensitive actions."""

    actor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_events',
    )
    action = models.CharField(max_length=100, db_index=True)
    target_type = models.CharField(max_length=50, blank=True, default='')
    target_id = models.CharField(max_length=64, blank=True, default='')
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [Index(fields=['action', '-created_at'])]

    def __str__(self):
        actor = self.actor.username if self.actor_id else 'system'
        return f'{self.created_at:%Y-%m-%d %H:%M} {actor} {self.action}'
