from django.db import models
import uuid

class Regla(models.Model):
    id_regla = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    descripcion = models.CharField(max_length=200)
    activa = models.BooleanField(default=True)

    class Meta:
        db_table = 'Regla'

    def __str__(self):
        return self.descripcion

class ReglaDetalle(models.Model):
    id_regla_detalle = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    regla = models.ForeignKey('rules.Regla', on_delete=models.CASCADE, related_name='detalles')
    usuario = models.ForeignKey('users.Usuario', on_delete=models.CASCADE, null=True, blank=True, related_name='reglas')
    observacion = models.CharField(max_length=200,null=True, blank=True)
    activa = models.BooleanField(default=True, )
    valor = models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=10)

    class Meta:
        db_table = 'ReglaDetalle'

