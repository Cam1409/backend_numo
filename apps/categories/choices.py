from django.db.models import TextChoices
class TipoCategoriaChoices(TextChoices):
    ING = "Ingreso", "Ingreso"
    GAS = "Gasto", "Gasto"
    ING_FIJO = "Ingreso_Fijo", "Ingreso_Fijo"
    GAS_FIJO = "Gasto_Fijo", "Gasto_Fijo"