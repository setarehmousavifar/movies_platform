from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Animation, Movie, Series


class StaticViewSitemap(Sitemap):
    priority = 0.6
    changefreq = 'weekly'

    def items(self):
        return [
            'home',
            'movie_list',
            'series_list',
            'animation_list',
            'top_movies',
            'top_series',
            'genre_list',
        ]

    def location(self, item):
        return reverse(item)


class MovieSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Movie.objects.order_by('-id')

    def lastmod(self, obj):
        return getattr(obj, 'ai_enriched_at', None)

    def location(self, obj):
        return reverse('movie_detail', args=[obj.pk])


class SeriesSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Series.objects.order_by('-id')

    def lastmod(self, obj):
        return getattr(obj, 'ai_enriched_at', None)

    def location(self, obj):
        return reverse('series_detail', args=[obj.pk])


class AnimationSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Animation.objects.order_by('-id')

    def lastmod(self, obj):
        return getattr(obj, 'ai_enriched_at', None)

    def location(self, obj):
        return reverse('animation_detail', args=[obj.pk])
