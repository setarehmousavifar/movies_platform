from datetime import date, timedelta

from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.db.models import Count, Q
from django.utils.html import format_html

from .models import (
    AgeRating,
    Actor,
    Animation,
    AuditLog,
    Category,
    Director,
    DownloadLink,
    Episode,
    FavoriteItem,
    Genre,
    Like,
    Movie,
    Notification,
    Playlist,
    PlaylistItem,
    Profile,
    Recommendation,
    Review,
    Season,
    Series,
    Subscription,
    Subtitle,
    Tag,
    User,
    UserGenrePreference,
    VideoQuality,
    WalletTransaction,
    WatchHistory,
    Watchlist,
)
from .services import EnrichmentService, SubscriptionService


def build_admin_dashboard():
    today = date.today()
    unenriched = (
        Movie.objects.filter(Q(ai_enriched_at__isnull=True) | Q(ai_summary='')).count()
        + Series.objects.filter(Q(ai_enriched_at__isnull=True) | Q(ai_summary='')).count()
        + Animation.objects.filter(Q(ai_enriched_at__isnull=True) | Q(ai_summary='')).count()
    )
    return {
        'mp_movie_count': Movie.objects.count(),
        'mp_series_count': Series.objects.count(),
        'mp_animation_count': Animation.objects.count(),
        'mp_active_premium': Subscription.objects.filter(
            subscription_type='premium',
            is_active=True,
            end_date__gte=today,
        ).count(),
        'mp_unread_notifications': Notification.objects.filter(is_read=False).count(),
        'mp_unenriched_count': unenriched,
        'mp_upgrade_requests': list(
            AuditLog.objects.filter(action='subscription.upgrade_requested')
            .select_related('actor')
            .order_by('-created_at')[:8]
        ),
    }


_original_index = admin.site.index


def _catalog_admin_index(request, extra_context=None):
    extra_context = extra_context or {}
    extra_context.update(build_admin_dashboard())
    return _original_index(request, extra_context)


admin.site.index = _catalog_admin_index
admin.site.index_template = 'admin/catalog_index.html'
admin.site.site_header = 'Movie Platform Admin'
admin.site.site_title = 'Movie Platform'
admin.site.index_title = 'Catalog operations'


class DownloadLinkInline(admin.TabularInline):
    model = DownloadLink
    extra = 1
    fields = ('quality', 'file_size', 'download_url')
    verbose_name_plural = 'Download links'


class SeasonInline(admin.TabularInline):
    model = Season
    extra = 0
    fields = ('season_number', 'description')
    show_change_link = True
    verbose_name_plural = 'Seasons'


class EpisodeInline(admin.TabularInline):
    model = Episode
    extra = 1
    fields = ('episode_number', 'title', 'duration')
    verbose_name_plural = 'Episodes'


class CatalogAIAdminMixin:
    actions = ('enrich_with_ai',)

    @admin.action(description='Enrich selected with AI summary/tags')
    def enrich_with_ai(self, request, queryset):
        count = 0
        for obj in queryset:
            EnrichmentService.enrich_instance(obj, force=True)
            count += 1
        self.message_user(request, f'Enriched {count} item(s).', messages.SUCCESS)


@admin.register(Movie)
class MovieAdmin(CatalogAIAdminMixin, admin.ModelAdmin):
    list_display = (
        'title',
        'release_date',
        'overall_rating',
        'view_count',
        'download_count',
        'ai_enriched_at',
    )
    list_filter = ('language', 'country', 'age_rating')
    search_fields = ('title', 'description', 'ai_summary')
    filter_horizontal = ('genres', 'directors', 'stars', 'tags')
    readonly_fields = ('ai_enriched_at',)
    date_hierarchy = 'release_date'
    ordering = ('-release_date', 'title')
    list_per_page = 25
    inlines = (DownloadLinkInline,)
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'title',
                    'release_date',
                    'description',
                    'duration',
                    'language',
                    'country',
                    'age_rating',
                    'overall_rating',
                    'view_count',
                    'poster_url',
                    'poster_image',
                    'background_poster',
                    'trailer_url',
                    'trailer_video',
                    'genres',
                    'directors',
                    'stars',
                    'tags',
                )
            },
        ),
        ('AI enrichment', {'fields': ('ai_summary', 'ai_tags', 'ai_enriched_at')}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_dl_count=Count('download_links'))

    @admin.display(description='Downloads', ordering='_dl_count')
    def download_count(self, obj):
        return getattr(obj, '_dl_count', obj.download_links.count())


@admin.register(Series)
class SeriesAdmin(CatalogAIAdminMixin, admin.ModelAdmin):
    list_display = (
        'title',
        'get_years',
        'status',
        'season_count',
        'episode_count',
        'overall_rating',
        'download_count',
        'ai_enriched_at',
    )
    list_filter = ('status', 'language', 'country', 'age_rating')
    search_fields = ('title', 'description', 'ai_summary')
    filter_horizontal = ('genres', 'directors', 'stars', 'tags')
    readonly_fields = ('ai_enriched_at',)
    ordering = ('-release_date', 'title')
    list_per_page = 25
    inlines = (SeasonInline, DownloadLinkInline)
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'title',
                    'release_date',
                    'description',
                    'duration',
                    'language',
                    'country',
                    'age_rating',
                    'overall_rating',
                    'view_count',
                    'start_year',
                    'end_year',
                    'status',
                    'season_count',
                    'episode_count',
                    'poster_url',
                    'poster_image',
                    'background_poster',
                    'trailer_url',
                    'trailer_video',
                    'genres',
                    'directors',
                    'stars',
                    'tags',
                )
            },
        ),
        ('AI enrichment', {'fields': ('ai_summary', 'ai_tags', 'ai_enriched_at')}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_dl_count=Count('download_links'))

    @admin.display(description='Downloads', ordering='_dl_count')
    def download_count(self, obj):
        return getattr(obj, '_dl_count', obj.download_links.count())


@admin.register(Animation)
class AnimationAdmin(CatalogAIAdminMixin, admin.ModelAdmin):
    list_display = (
        'title',
        'release_date',
        'overall_rating',
        'view_count',
        'download_count',
        'ai_enriched_at',
    )
    list_filter = ('language', 'country', 'age_rating')
    search_fields = ('title', 'description', 'ai_summary')
    filter_horizontal = ('genres', 'directors', 'stars', 'tags')
    readonly_fields = ('ai_enriched_at',)
    date_hierarchy = 'release_date'
    ordering = ('-release_date', 'title')
    list_per_page = 25
    inlines = (DownloadLinkInline,)
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'title',
                    'release_date',
                    'description',
                    'duration',
                    'language',
                    'country',
                    'age_rating',
                    'overall_rating',
                    'view_count',
                    'poster_url',
                    'poster_image',
                    'background_poster',
                    'trailer_url',
                    'trailer_video',
                    'genres',
                    'directors',
                    'stars',
                    'tags',
                )
            },
        ),
        ('AI enrichment', {'fields': ('ai_summary', 'ai_tags', 'ai_enriched_at')}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_dl_count=Count('download_links'))

    @admin.display(description='Downloads', ordering='_dl_count')
    def download_count(self, obj):
        return getattr(obj, '_dl_count', obj.download_links.count())


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('series', 'season_number', 'episode_total')
    list_filter = ('series',)
    search_fields = ('series__title',)
    ordering = ('series__title', 'season_number')
    inlines = (EpisodeInline,)
    autocomplete_fields = ('series',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('series').annotate(
            _ep_count=Count('episodes')
        )

    @admin.display(description='Episodes', ordering='_ep_count')
    def episode_total(self, obj):
        return getattr(obj, '_ep_count', obj.episodes.count())


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('title', 'season', 'episode_number', 'duration')
    list_filter = ('season__series',)
    search_fields = ('title', 'season__series__title')
    autocomplete_fields = ('season',)
    ordering = ('season__series__title', 'season__season_number', 'episode_number')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'target_title', 'rating', 'parent', 'review_date')
    list_filter = ('rating', 'review_date')
    search_fields = ('user__username', 'review_text')
    date_hierarchy = 'review_date'


@admin.register(FavoriteItem)
class FavoriteItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'series', 'animation', 'added_date')
    list_filter = ('added_date',)
    search_fields = ('user__username', 'movie__title', 'series__title', 'animation__title')
    autocomplete_fields = ('user', 'movie', 'series', 'animation')


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'series', 'animation', 'added_date')
    list_filter = ('added_date',)
    search_fields = ('user__username', 'movie__title', 'series__title', 'animation__title')
    autocomplete_fields = ('user', 'movie', 'series', 'animation')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'subscription_type',
        'start_date',
        'end_date',
        'is_active',
        'premium_status',
    )
    list_filter = ('subscription_type', 'is_active', 'end_date')
    search_fields = ('user__username', 'user__email')
    autocomplete_fields = ('user',)
    date_hierarchy = 'end_date'
    actions = ('grant_premium_30_days', 'deactivate_subscriptions')

    @admin.display(description='User premium flag')
    def premium_status(self, obj):
        flag = obj.user.is_premium
        return format_html(
            '<span style="color:{};">{}</span>',
            '#0a7' if flag else '#a40',
            'yes' if flag else 'no',
        )

    @admin.action(description='Grant premium (30 days) via billing service')
    def grant_premium_30_days(self, request, queryset):
        users = {sub.user_id: sub.user for sub in queryset.select_related('user')}
        count = 0
        for user in users.values():
            SubscriptionService.assign(
                user=user,
                actor=request.user,
                subscription_type='premium',
                end_date=date.today() + timedelta(days=30),
                reason='admin_bulk_grant',
            )
            count += 1
        self.message_user(
            request,
            f'Granted 30-day premium to {count} user(s).',
            messages.SUCCESS,
        )

    @admin.action(description='Deactivate selected subscriptions')
    def deactivate_subscriptions(self, request, queryset):
        user_ids = list(queryset.values_list('user_id', flat=True).distinct())
        updated = queryset.update(is_active=False)
        for user in User.objects.filter(pk__in=user_ids):
            user.sync_premium_flag()
        self.message_user(request, f'Deactivated {updated} subscription(s).', messages.WARNING)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'actor', 'action', 'target_type', 'target_id', 'note_preview')
    list_filter = ('action', 'created_at')
    search_fields = ('action', 'target_id', 'actor__username')
    readonly_fields = ('actor', 'action', 'target_type', 'target_id', 'metadata', 'created_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    @admin.display(description='note')
    def note_preview(self, obj):
        note = (obj.metadata or {}).get('note') or ''
        return note[:60] or '—'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message_preview', 'is_read', 'sent_date')
    list_filter = ('is_read', 'sent_date')
    search_fields = ('message', 'user__username')
    autocomplete_fields = ('user',)
    date_hierarchy = 'sent_date'
    actions = ('mark_as_read', 'mark_as_unread')

    @admin.display(description='message')
    def message_preview(self, obj):
        return (obj.message or '')[:60]

    @admin.action(description='Mark selected as read')
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'Marked {updated} notification(s) read.', messages.SUCCESS)

    @admin.action(description='Mark selected as unread')
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'Marked {updated} notification(s) unread.', messages.SUCCESS)


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'recommended_date')
    list_filter = ('recommended_date',)
    search_fields = ('user__username', 'movie__title')
    autocomplete_fields = ('user', 'movie')
    date_hierarchy = 'recommended_date'


@admin.register(DownloadLink)
class DownloadLinkAdmin(admin.ModelAdmin):
    list_display = ('target_title', 'quality', 'file_size', 'movie', 'series', 'animation')
    list_filter = ('quality',)
    search_fields = (
        'movie__title',
        'series__title',
        'animation__title',
        'download_url',
    )
    autocomplete_fields = ('movie', 'series', 'animation')


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = (
        'username',
        'email',
        'is_staff',
        'is_premium',
        'is_active',
        'date_joined',
    )
    list_filter = ('is_staff', 'is_premium', 'is_active', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    actions = ('grant_premium_30_days',)

    fieldsets = DjangoUserAdmin.fieldsets + (
        ('Catalog flags', {'fields': ('is_premium', 'phone_number', 'profile_picture')}),
    )
    readonly_fields = ()

    @admin.action(description='Grant premium (30 days) via billing service')
    def grant_premium_30_days(self, request, queryset):
        count = 0
        for user in queryset:
            SubscriptionService.assign(
                user=user,
                actor=request.user,
                subscription_type='premium',
                end_date=date.today() + timedelta(days=30),
                reason='admin_user_bulk_grant',
            )
            count += 1
        self.message_user(
            request,
            f'Granted 30-day premium to {count} user(s).',
            messages.SUCCESS,
        )


admin.site.register(AgeRating)
admin.site.register(Genre)
admin.site.register(Actor)
admin.site.register(Director)
admin.site.register(Tag)
admin.site.register(WalletTransaction)
admin.site.register(WatchHistory)
admin.site.register(Subtitle)
admin.site.register(VideoQuality)
admin.site.register(Like)
admin.site.register(Playlist)
admin.site.register(PlaylistItem)
admin.site.register(UserGenrePreference)
admin.site.register(Profile)
admin.site.register(Category)
