from django.apps import AppConfig


class CategoriesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.categories'
    def ready(self):
        print("🔥 [CategoriesConfig.ready] Señales de categories se están cargando...")
        import apps.categories.signals