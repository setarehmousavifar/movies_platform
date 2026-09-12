from .models import Genre, Notification


def nav_genres(request):
    """Expose genres to all templates (navbar dropdown)."""
    return {'genres': Genre.objects.all()}


def nav_notifications(request):
    """Unread notification count for authenticated users."""
    if not getattr(request, 'user', None) or not request.user.is_authenticated:
        return {'unread_notification_count': 0}
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return {'unread_notification_count': count}
