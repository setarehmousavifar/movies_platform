"""Advanced catalog search (Postgres full-text when available)."""

from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db import connection
from django.db.models import Q

from main.models import Animation, Movie, Series


class SearchService:
    @staticmethod
    def _is_postgres() -> bool:
        return connection.vendor == 'postgresql'

    @classmethod
    def search_movies(cls, query: str, limit: int = 20):
        query = (query or '').strip()
        if not query:
            return Movie.objects.none()
        if cls._is_postgres():
            vector = SearchVector('title', weight='A') + SearchVector('description', weight='B')
            search_query = SearchQuery(query)
            return (
                Movie.objects.annotate(rank=SearchRank(vector, search_query))
                .filter(rank__gte=0.05)
                .order_by('-rank', '-overall_rating')[:limit]
            )
        return Movie.objects.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(tags__name__icontains=query)
            | Q(genres__genre_name__icontains=query)
        ).distinct().order_by('-overall_rating', '-view_count')[:limit]

    @classmethod
    def search_series(cls, query: str, limit: int = 10):
        query = (query or '').strip()
        if not query:
            return Series.objects.none()
        if cls._is_postgres():
            vector = SearchVector('title', weight='A') + SearchVector('description', weight='B')
            search_query = SearchQuery(query)
            return (
                Series.objects.annotate(rank=SearchRank(vector, search_query))
                .filter(rank__gte=0.05)
                .order_by('-rank', '-overall_rating')[:limit]
            )
        return Series.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | Q(genres__genre_name__icontains=query)
        ).distinct().order_by('-overall_rating', '-view_count')[:limit]

    @classmethod
    def search_animations(cls, query: str, limit: int = 10):
        query = (query or '').strip()
        if not query:
            return Animation.objects.none()
        if cls._is_postgres():
            vector = SearchVector('title', weight='A') + SearchVector('description', weight='B')
            search_query = SearchQuery(query)
            return (
                Animation.objects.annotate(rank=SearchRank(vector, search_query))
                .filter(rank__gte=0.05)
                .order_by('-rank', '-overall_rating')[:limit]
            )
        return Animation.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | Q(genres__genre_name__icontains=query)
        ).distinct().order_by('-overall_rating', '-view_count')[:limit]

    @classmethod
    def search_all(cls, query: str):
        results = []
        for movie in cls.search_movies(query):
            results.append(
                {
                    'type': 'movie',
                    'id': movie.id,
                    'title': movie.title,
                    'overall_rating': movie.overall_rating,
                    'poster': movie.get_poster(),
                    'ai_summary': movie.ai_summary or None,
                }
            )
        for series in cls.search_series(query):
            results.append(
                {
                    'type': 'series',
                    'id': series.id,
                    'title': series.title,
                    'overall_rating': series.overall_rating,
                    'poster': series.get_poster(),
                    'ai_summary': series.ai_summary or None,
                }
            )
        for animation in cls.search_animations(query):
            results.append(
                {
                    'type': 'animation',
                    'id': animation.id,
                    'title': animation.title,
                    'overall_rating': animation.overall_rating,
                    'poster': animation.get_poster(),
                    'ai_summary': animation.ai_summary or None,
                }
            )
        return results
