"""Content-based recommendations using genres, preferences, and favorites."""

from collections import Counter

from django.db.models import Count

from main.models import FavoriteItem, Movie, UserGenrePreference


class RecommendationService:
    @classmethod
    def recommend_movies(cls, user, limit: int = 10):
        """Return ranked movies. Read-only — no DB writes on the GET path."""
        if not user.is_authenticated:
            return list(
                Movie.objects.order_by('-overall_rating', '-view_count')[:limit]
            )

        genre_scores = Counter()
        for pref in UserGenrePreference.objects.filter(user=user).select_related('genre'):
            genre_scores[pref.genre_id] += pref.preference_level

        fav_movie_ids = list(
            FavoriteItem.objects.filter(user=user, movie__isnull=False).values_list(
                'movie_id', flat=True
            )
        )
        for movie in Movie.objects.filter(id__in=fav_movie_ids).prefetch_related('genres'):
            for genre in movie.genres.all():
                genre_scores[genre.id] += 3

        excluded = set(fav_movie_ids)
        if not genre_scores:
            return list(
                Movie.objects.exclude(id__in=excluded)
                .order_by('-overall_rating', '-view_count')[:limit]
            )

        top_genre_ids = [gid for gid, _ in genre_scores.most_common(5)]
        qs = (
            Movie.objects.filter(genres__id__in=top_genre_ids)
            .exclude(id__in=excluded)
            .annotate(overlap=Count('genres', distinct=True))
            .order_by('-overlap', '-overall_rating', '-view_count')
            .distinct()[:limit]
        )
        return list(qs)
