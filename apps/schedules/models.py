from django.db import models
import uuid

class ProgramacionGasto(models.Model):
    id_programacion = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario   = models.ForeignKey('users.Usuario', on_delete=models.CASCADE, related_name='programaciones')
    periodo   = models.ForeignKey('period.Periodo', on_delete=models.PROTECT, related_name='programaciones')
    categoria = models.ForeignKey('categories.Categoria', on_delete=models.PROTECT, related_name='programaciones')
    nombre = models.CharField(max_length=120)
    fecha_planificada = models.DateField()
    realizado_en_fecha = models.BooleanField(null=True, blank=True)
    fecha_real = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'ProgramacionGasto'

    def __str__(self):
        return self.nombre

