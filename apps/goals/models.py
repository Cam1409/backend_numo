from django.db import models
from django.core.validators import MinValueValidator
import uuid

class Objetivo(models.Model):
    class Estado(models.TextChoices):
        EN_PROGRESO = 'EN_PROGRESO', 'En progreso'
        CUMPLIDO    = 'CUMPLIDO', 'Cumplido'
        CANCELADO   = 'CANCELADO', 'Cancelado'

    id_objetivo = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey('users.Usuario', on_delete=models.CASCADE, related_name='objetivos')
    nombre = models.CharField(max_length=120)
    monto_meta = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    fecha_objetivo = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.EN_PROGRESO)

    class Meta:
        db_table = 'Objetivo'

    def __str__(self):
        return self.nombre
