# taskify_core/apps.py
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'taskify_core'
    
    def ready(self):
        try:
            from . import signals  # noqa: F401
        except Exception:
            pass
