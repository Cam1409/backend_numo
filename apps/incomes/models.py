from django.db import models
import uuid
from decimal import Decimal
from apps.users.models import Usuario
from apps.frequency.models import Frecuencia

class IngresoFijo(models.Model):
    id_ingreso_fijo = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='ingresos_fijos')

    nombre = models.CharField(max_length=80, default='Sueldo')
    monto = models.DecimalField(max_digits=12, decimal_places=2)

    frecuencia = models.ForeignKey(Frecuencia, on_delete=models.PROTECT, related_name='ingresos')
    fecha_inicio = models.DateField(null=True, blank=True)
    dia_corte = models.PositiveSmallIntegerField(null=True, blank=True)

    es_principal = models.BooleanField(default=True)
    activo = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Ingreso_fijo'
        indexes = [models.Index(fields=['usuario', 'activo'])]

    def __str__(self):
        return f'{self.usuario} - {self.nombre} ({self.frecuencia.descripcion})'

    @property
    def monto_mensual_equivalente(self) -> Decimal:
        f = (self.frecuencia.descripcion or '').upper()
        if f == 'DIARIO':     factor = Decimal('30')
        elif f == 'SEMANAL':  factor = Decimal('4.345')
        elif f == 'QUINCENAL':factor = Decimal('2')
        else:                 factor = Decimal('1')
        return (self.monto * factor).quantize(Decimal('0.01'))
