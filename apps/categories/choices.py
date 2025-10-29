from django.db.models import TextChoices
class TipoCategoriaChoices(TextChoices):
    ING = "Ingreso", "Ingreso"
    GAS = "Gasto", "Gasto"
    ING_FIJO = "Ingreso Fijo", "Ingreso Fijo"
    GAS_FIJO = "Gasto Fijo", "Gasto Fijo"