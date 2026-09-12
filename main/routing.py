from django.urls import path

from main.consumers import BreakingAlertConsumer

websocket_urlpatterns = [
    path('ws/alerts/', BreakingAlertConsumer.as_asgi()),
]
