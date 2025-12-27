from django.apps import AppConfig


class EventsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'events'

    def ready(self):
        """Initialize cache invalidation signals when app is ready."""
        from .cache import setup_cache_invalidation_signals
        setup_cache_invalidation_signals()
