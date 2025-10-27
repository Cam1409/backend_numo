from django.db import models
import uuid
from apps.users.models import Usuario

class Frecuencia(models.Model):
    id_frecuencia = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    descripcion = models.CharField(max_length=50, unique=True, default='UNSET')


    class Meta:
        db_table = 'Frecuencia'

    def __str__(self):
        return self.descripcion

class FrecuenciaFija(models.Model):
    id_frecuencia_fija = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # 1 frecuencia fija por usuario
    usuario = models.OneToOneField(
        Usuario, on_delete=models.CASCADE, related_name='frecuencia_fija'
    )
    # catálogo de frecuencias (DIARIO/SEMANAL/QUINCENAL/MENSUAL)
    frecuencia = models.ForeignKey(
        Frecuencia, on_delete=models.PROTECT, related_name='usuarios_frecuencia_fija', null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Frecuencia_fija'
        verbose_name = 'Frecuencia fija'
        verbose_name_plural = 'Frecuencias fijas'

    def __str__(self):
        return f'{self.usuario} -> {self.frecuencia.descripcion}'