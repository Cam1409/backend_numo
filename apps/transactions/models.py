from django.db import models
from django.core.validators import MinValueValidator
import uuid

class Transaccion(models.Model):
    id_transaccion = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey('users.Usuario', on_delete=models.CASCADE, related_name='transacciones')
    periodo = models.ForeignKey('period.Periodo', on_delete=models.PROTECT, related_name='transacciones')
    categoria = models.ForeignKey('categories.Categoria', on_delete=models.PROTECT, related_name='transacciones')
    descripcion = models.CharField(max_length=200, null=True, blank=True)
    monto = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    fecha_transaccion = models.DateField()
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Transaccion'
        indexes = [models.Index(fields=['usuario', 'periodo'], name='ix_trans_usuario_periodo')]

    def __str__(self):
        return f'{self.descripcion or "Transacción"} - {self.monto}'
