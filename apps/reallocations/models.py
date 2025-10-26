from django.db import models
from django.core.validators import MinValueValidator
import uuid

class ReasignacionPresupuestal(models.Model):
    id_reasignacion = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey('users.Usuario', on_delete=models.CASCADE, related_name='reasignaciones')
    periodo = models.ForeignKey('period.Periodo', on_delete=models.PROTECT, related_name='reasignaciones')
    fecha_ajuste = models.DateTimeField(auto_now_add=True)
    categoria_desde = models.ForeignKey('categories.Categoria', on_delete=models.PROTECT, null=True, blank=True, related_name='salientes')
    categoria_hacia = models.ForeignKey('categories.Categoria', on_delete=models.PROTECT, null=True, blank=True, related_name='entrantes')
    monto = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    motivo = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = 'ReasignacionPresupuestal'

    def __str__(self):
        return f'{self.usuario_id} {self.periodo_id} {self.monto}'
