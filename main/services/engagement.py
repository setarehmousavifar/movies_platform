"""Engagement domain services (future app: engagement)."""

from django.db import transaction

from main.exceptions import PermissionDeniedError, ValidationDomainError
from main.models import FavoriteItem, Movie, Review, Watchlist


class ReviewService:
    @staticmethod
    def _scoped_parent(parent_id, *, movie=None, series=None, animation=None):
        if not parent_id:
            return None
        filters = {'id': parent_id, 'parent__isnull': True}
        if movie is not None:
            filters['movie'] = movie
        elif series is not None:
            filters['series'] = series
        elif animation is not None:
            filters['animation'] = animation
        try:
            return Review.objects.get(**filters)
        except Review.DoesNotExist as exc:
            raise ValidationDomainError('Invalid parent_id for this catalog item.') from exc

    @classmethod
    @transaction.atomic
    def create_review(cls, *, user, rating, review_text, movie=None, series=None, animation=None, parent_id=None):
        if not user.is_authenticated:
            raise PermissionDeniedError('Login required to post a review.')
        targets = [movie, series, animation]
        if sum(t is not None for t in targets) != 1:
            raise ValidationDomainError('Review must target exactly one catalog item.')
        parent = cls._scoped_parent(
            parent_id, movie=movie, series=series, animation=animation
        )
        review = Review(
            user=user,
            movie=movie,
            series=series,
            animation=animation,
            rating=rating,
            review_text=review_text,
            parent=parent,
        )
        review.full_clean()
        review.save()
        return review

    @classmethod
    @transaction.atomic
    def create_reply(cls, *, user, parent_review: Review, reply_text: str):
        if not user.is_authenticated:
            raise PermissionDeniedError('Login required to reply.')
        if not reply_text or not reply_text.strip():
            raise ValidationDomainError('Reply text is required.')
        reply = Review(
            user=user,
            movie=parent_review.movie,
            series=parent_review.series,
            animation=parent_review.animation,
            parent=parent_review,
            rating=parent_review.rating,
            review_text=reply_text.strip(),
        )
        reply.full_clean()
        reply.save()
        return reply


class FavoriteService:
    @staticmethod
    def is_favorite_movie(user, movie: Movie) -> bool:
        if not user.is_authenticated:
            return False
        return FavoriteItem.objects.filter(user=user, movie=movie).exists()

    @staticmethod
    def is_favorite_series(user, series) -> bool:
        if not user.is_authenticated:
            return False
        return FavoriteItem.objects.filter(user=user, series=series).exists()

    @staticmethod
    def is_favorite_animation(user, animation) -> bool:
        if not user.is_authenticated:
            return False
        return FavoriteItem.objects.filter(user=user, animation=animation).exists()

    @staticmethod
    @transaction.atomic
    def add_movie(user, movie: Movie):
        if not user.is_authenticated:
            raise PermissionDeniedError('Login required.')
        item, created = FavoriteItem.objects.get_or_create(user=user, movie=movie)
        return item, created

    @staticmethod
    @transaction.atomic
    def add_item(user, *, movie=None, series=None, animation=None):
        if not user.is_authenticated:
            raise PermissionDeniedError('Login required.')
        targets = [movie, series, animation]
        if sum(t is not None for t in targets) != 1:
            raise ValidationDomainError('Provide exactly one of movie, series, or animation.')
        if movie is not None:
            return FavoriteItem.objects.get_or_create(user=user, movie=movie)
        if series is not None:
            return FavoriteItem.objects.get_or_create(user=user, series=series)
        return FavoriteItem.objects.get_or_create(user=user, animation=animation)

    @staticmethod
    @transaction.atomic
    def remove_movie(user, movie: Movie):
        if not user.is_authenticated:
            raise PermissionDeniedError('Login required.')
        FavoriteItem.objects.filter(user=user, movie=movie).delete()

    @staticmethod
    @transaction.atomic
    def remove_item(user, *, movie=None, series=None, animation=None):
        if not user.is_authenticated:
            raise PermissionDeniedError('Login required.')
        targets = [movie, series, animation]
        if sum(t is not None for t in targets) != 1:
            raise ValidationDomainError('Provide exactly one of movie, series, or animation.')
        qs = FavoriteItem.objects.filter(user=user)
        if movie is not None:
            qs.filter(movie=movie).delete()
        elif series is not None:
            qs.filter(series=series).delete()
        else:
            qs.filter(animation=animation).delete()

    @staticmethod
    def list_for(user):
        return FavoriteItem.objects.filter(user=user).select_related(
            'movie', 'series', 'animation'
        )


class WatchlistService:
    @staticmethod
    def is_watchlist_movie(user, movie: Movie) -> bool:
        if not user.is_authenticated:
            return False
        return Watchlist.objects.filter(user=user, movie=movie).exists()

    @staticmethod
    def is_watchlist_series(user, series) -> bool:
        if not user.is_authenticated:
            return False
        return Watchlist.objects.filter(user=user, series=series).exists()

    @staticmethod
    def is_watchlist_animation(user, animation) -> bool:
        if not user.is_authenticated:
            return False
        return Watchlist.objects.filter(user=user, animation=animation).exists()

    @staticmethod
    @transaction.atomic
    def add_movie(user, movie: Movie):
        if not user.is_authenticated:
            raise PermissionDeniedError('Login required.')
        item, created = Watchlist.objects.get_or_create(user=user, movie=movie)
        return item, created

    @staticmethod
    @transaction.atomic
    def add_item(user, *, movie=None, series=None, animation=None):
        if not user.is_authenticated:
            raise PermissionDeniedError('Login required.')
        targets = [movie, series, animation]
        if sum(t is not None for t in targets) != 1:
            raise ValidationDomainError('Provide exactly one of movie, series, or animation.')
        if movie is not None:
            return Watchlist.objects.get_or_create(user=user, movie=movie)
        if series is not None:
            return Watchlist.objects.get_or_create(user=user, series=series)
        return Watchlist.objects.get_or_create(user=user, animation=animation)

    @staticmethod
    @transaction.atomic
    def remove_movie(user, movie: Movie):
        if not user.is_authenticated:
            raise PermissionDeniedError('Login required.')
        Watchlist.objects.filter(user=user, movie=movie).delete()

    @staticmethod
    @transaction.atomic
    def remove_item(user, *, movie=None, series=None, animation=None):
        if not user.is_authenticated:
            raise PermissionDeniedError('Login required.')
        targets = [movie, series, animation]
        if sum(t is not None for t in targets) != 1:
            raise ValidationDomainError('Provide exactly one of movie, series, or animation.')
        qs = Watchlist.objects.filter(user=user)
        if movie is not None:
            qs.filter(movie=movie).delete()
        elif series is not None:
            qs.filter(series=series).delete()
        else:
            qs.filter(animation=animation).delete()

    @staticmethod
    def list_for(user):
        return Watchlist.objects.filter(user=user).select_related(
            'movie', 'series', 'animation'
        )
