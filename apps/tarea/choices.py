from django.db.models import TextChoices
class TipoEstado(TextChoices):
    PENDIENTE = "Pendiente",  "Pendiente"
    REALIZADO = "Realizado", "Realizado"