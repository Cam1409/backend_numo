from django.apps import AppConfig
from django.db.models.signals import post_migrate

class FrequencyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.frequency'
    verbose_name = 'Frequency'

    def ready(self):
        # Cargar DIARIO/SEMANAL/QUINCENAL/MENSUAL después de migrate
        from django.db.utils import OperationalError, ProgrammingError
        from .models import Frecuencia

        def create_presets(sender, **kwargs):
            presets = ['DIARIO', 'SEMANAL', 'QUINCENAL', 'MENSUAL']
            try:
                for desc in presets:
                    Frecuencia.objects.get_or_create(descripcion=desc)
            except (OperationalError, ProgrammingError):
                pass

        post_migrate.connect(create_presets, sender=self)
