from django.db import models
from django.core.validators import MinValueValidator
import uuid

class Presupuesto(models.Model):
    id_presupuesto = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario   = models.ForeignKey('users.Usuario', on_delete=models.CASCADE, related_name='presupuestos')
    periodo   = models.ForeignKey('period.Periodo', on_delete=models.PROTECT, related_name='presupuestos')
    frecuencia = models.ForeignKey('frequency.Frecuencia', on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Presupuesto'
        unique_together = (('usuario', 'periodo'),)

class PresupuestoItem(models.Model):
    id_item = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    presupuesto = models.ForeignKey('budget.Presupuesto', on_delete=models.CASCADE, related_name='items')
    categoria   = models.ForeignKey('categories.Categoria', on_delete=models.PROTECT, related_name='items_presupuesto')
    monto_planificado = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])

    class Meta:
        db_table = 'PresupuestoItem'
