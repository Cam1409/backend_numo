from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

class Periodo(models.Model):
    id_periodo   = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    anio         = models.PositiveIntegerField()
    mes          = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    fecha_inicio = models.DateField()
    fecha_fin    = models.DateField()

    class Meta:
        db_table = 'Periodo'
        unique_together = (('anio', 'mes'),)
        indexes = [models.Index(fields=['anio', 'mes'], name='idx_periodo_aniomes')]

    def __str__(self):
        return f'{self.anio}-{str(self.mes).zfill(2)}'
