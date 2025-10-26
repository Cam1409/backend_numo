from django.db.models import TextChoices
class TipoCategoriaChoices(TextChoices):
    ING = "Ingreso", "Ingreso"
    GAS = "Gasto", "Gasto"