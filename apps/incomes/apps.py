# apps/incomes/apps.py
from django.apps import AppConfig

class IncomesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.incomes'
    label = 'app_incomes'
    verbose_name = 'Incomes'

    def ready(self):
        # No importes modelos aquí a menos que sea estrictamente necesario.
        # Si algún día necesitas conectar señales:
        #   from . import signals
        # O importar modelos dentro de ready() (no en el módulo).
        pass
