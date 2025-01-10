from django.contrib import admin

from .models import (
    User, AgeRating, Movie, Genre, Actor, MovieActor, MovieGenre, 
    WalletTransaction, Subscription, Review, WatchHistory, 
    FavoriteMovie, Notification, DownloadLink, Subtitle, Tag, 
    MovieTag, VideoQuality, Reply, Director, MovieDirector, 
    Season, Episode, Like, Playlist, PlaylistItem, 
    Recommendation, UserGenrePreference
)

from .models import Movie, Series, Animation

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_date', 'overall_rating')
    list_filter = ('language', 'country')
    search_fields = ('title',)
    filter_horizontal = ('genres',)

@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ('title', 'rating', 'release_date')

@admin.register(Animation)
class AnimationAdmin(admin.ModelAdmin):
    list_display = ['title', 'release_date']

# ثبت مدل‌ها در پنل مدیریت
admin.site.register(User)
admin.site.register(AgeRating)
admin.site.register(Genre)
admin.site.register(Actor)
admin.site.register(MovieActor)
admin.site.register(MovieGenre)
admin.site.register(WalletTransaction)
admin.site.register(Subscription)
admin.site.register(Review)
admin.site.register(WatchHistory)
admin.site.register(FavoriteMovie)
admin.site.register(Notification)
admin.site.register(DownloadLink)
admin.site.register(Subtitle)
admin.site.register(Tag)
admin.site.register(MovieTag)
admin.site.register(VideoQuality)
admin.site.register(Reply)
admin.site.register(Director)
admin.site.register(MovieDirector)
admin.site.register(Season)
admin.site.register(Episode)
admin.site.register(Like)
admin.site.register(Playlist)
admin.site.register(PlaylistItem)
admin.site.register(Recommendation)
admin.site.register(UserGenrePreference)

