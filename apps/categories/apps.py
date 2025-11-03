from django.apps import AppConfig


class CategoriesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.categories'
    def ready(self):
        # Import para registrar las señales
        from . import signals  # noqa: F401