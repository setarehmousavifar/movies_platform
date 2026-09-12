"""Catalog domain services (future app: catalog)."""

from django.db.models import F


class ViewCountService:
    @staticmethod
    def bump(model, pk: int) -> None:
        model.objects.filter(pk=pk).update(view_count=F('view_count') + 1)
