import logging

from django.db import connection
from django.http import JsonResponse
from django.views.decorators.http import require_GET

logger = logging.getLogger('api.health')


@require_GET
def healthz(request):
    """Liveness/readiness probe for load balancers and Docker healthchecks."""
    db_ok = False
    try:
        connection.ensure_connection()
        db_ok = True
    except Exception as exc:  # noqa: BLE001
        logger.exception('healthz database check failed: %s', exc)

    payload = {
        'status': 'ok' if db_ok else 'degraded',
        'database': 'up' if db_ok else 'down',
    }
    return JsonResponse(payload, status=200 if db_ok else 503)
