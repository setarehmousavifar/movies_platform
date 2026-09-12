"""Breaking / catalog alerts via Notification rows + optional Channels broadcast."""

from __future__ import annotations

import logging

from asgiref.sync import async_to_sync
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver

from main.models import Animation, Movie, Notification, Series

logger = logging.getLogger('main.alerts')
User = get_user_model()


class AlertService:
    @staticmethod
    def notify_breaking(title: str, content_type: str, content_id: int, message: str | None = None):
        text = message or f'New {content_type} published: {title}'
        # Prefer staff recipients to keep seed/demo volume bounded.
        recipients = User.objects.filter(is_active=True).filter(
            Q(is_staff=True) | Q(is_superuser=True)
        )
        Notification.objects.bulk_create(
            [
                Notification(user=user, message=text, is_read=False)
                for user in recipients.iterator(chunk_size=100)
            ],
            batch_size=100,
        )
        AlertService._broadcast_ws(
            {
                'type': 'breaking.alert',
                'content_type': content_type,
                'content_id': content_id,
                'title': title,
                'message': text,
            }
        )
        logger.info('breaking_alert type=%s id=%s title=%s', content_type, content_id, title)

    @staticmethod
    def _broadcast_ws(payload: dict):
        try:
            from channels.layers import get_channel_layer

            channel_layer = get_channel_layer()
            if channel_layer is None:
                return
            async_to_sync(channel_layer.group_send)(
                'breaking_alerts',
                {'type': 'breaking.message', 'payload': payload},
            )
        except Exception:  # noqa: BLE001
            logger.debug('websocket broadcast skipped', exc_info=True)

    @staticmethod
    def recent_for(user, limit: int = 20):
        return Notification.objects.filter(user=user).order_by('-sent_date')[:limit]

    @staticmethod
    def mark_read(user, notification_id: int) -> bool:
        updated = Notification.objects.filter(user=user, id=notification_id, is_read=False).update(
            is_read=True
        )
        return bool(updated)


def _alerts_enabled() -> bool:
    return getattr(settings, 'CATALOG_ALERTS_ENABLED', True)


@receiver(post_save, sender=Movie)
def movie_created_alert(sender, instance, created, **kwargs):
    if created and _alerts_enabled():
        AlertService.notify_breaking(instance.title, 'movie', instance.pk)


@receiver(post_save, sender=Series)
def series_created_alert(sender, instance, created, **kwargs):
    if created and _alerts_enabled():
        AlertService.notify_breaking(instance.title, 'series', instance.pk)


@receiver(post_save, sender=Animation)
def animation_created_alert(sender, instance, created, **kwargs):
    if created and _alerts_enabled():
        AlertService.notify_breaking(instance.title, 'animation', instance.pk)
