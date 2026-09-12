from django.contrib import admin, messages

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
from .services import EnrichmentService


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
    list_display = ('title', 'release_date', 'overall_rating', 'view_count', 'ai_enriched_at')
    list_filter = ('language', 'country')
    search_fields = ('title', 'description', 'ai_summary')
    filter_horizontal = ('genres', 'directors', 'stars', 'tags')
    readonly_fields = ('ai_enriched_at',)
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


@admin.register(Series)
class SeriesAdmin(CatalogAIAdminMixin, admin.ModelAdmin):
    list_display = (
        'title',
        'get_years',
        'status',
        'season_count',
        'episode_count',
        'overall_rating',
        'ai_enriched_at',
    )
    list_filter = ('status', 'language', 'country')
    search_fields = ('title', 'description', 'ai_summary')
    filter_horizontal = ('genres', 'directors', 'stars', 'tags')
    readonly_fields = ('ai_enriched_at',)
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


@admin.register(Animation)
class AnimationAdmin(CatalogAIAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'release_date', 'overall_rating', 'view_count', 'ai_enriched_at')
    list_filter = ('language', 'country')
    search_fields = ('title', 'description', 'ai_summary')
    filter_horizontal = ('genres', 'directors', 'stars', 'tags')
    readonly_fields = ('ai_enriched_at',)
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


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('series', 'season_number')
    list_filter = ('series',)


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('title', 'season', 'episode_number', 'duration')
    list_filter = ('season__series',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'target_title', 'rating', 'parent', 'review_date')
    list_filter = ('rating',)


@admin.register(FavoriteItem)
class FavoriteItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'series', 'animation', 'added_date')


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'series', 'animation', 'added_date')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscription_type', 'start_date', 'end_date', 'is_active')
    list_filter = ('subscription_type', 'is_active')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'actor', 'action', 'target_type', 'target_id')
    list_filter = ('action',)
    search_fields = ('action', 'target_id', 'actor__username')
    readonly_fields = ('actor', 'action', 'target_type', 'target_id', 'metadata', 'created_at')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message_preview', 'is_read', 'sent_date')
    list_filter = ('is_read', 'sent_date')
    search_fields = ('message', 'user__username')

    @admin.display(description='message')
    def message_preview(self, obj):
        return (obj.message or '')[:60]


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'recommended_date')
    list_filter = ('recommended_date',)
    search_fields = ('user__username', 'movie__title')


admin.site.register(User)
admin.site.register(AgeRating)
admin.site.register(Genre)
admin.site.register(Actor)
admin.site.register(Director)
admin.site.register(Tag)
admin.site.register(WalletTransaction)
admin.site.register(WatchHistory)
admin.site.register(DownloadLink)
admin.site.register(Subtitle)
admin.site.register(VideoQuality)
admin.site.register(Like)
admin.site.register(Playlist)
admin.site.register(PlaylistItem)
admin.site.register(UserGenrePreference)
admin.site.register(Profile)
admin.site.register(Category)
