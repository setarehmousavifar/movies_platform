from django.apps import AppConfig


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):
        import main.signals  # noqa: F401
        import main.services.alerts  # noqa: F401 — register catalog alert signals
