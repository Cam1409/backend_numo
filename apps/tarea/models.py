from django.db import models
import uuid
from apps.tarea.choices import TipoEstado


class Tarea(models.Model):
    idTarea = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        "users.Usuario", on_delete=models.CASCADE, null=True, blank=True
    )
    nombre = models.CharField(max_length=200, null=True, blank=True)
    fechaProgramada = models.DateField(null=True, blank=True)
    fechaEjecutada = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=200, null=True, blank=True, choices=TipoEstado.choices, default=TipoEstado.PENDIENTE)

    class Meta:
        db_table = "Tarea"
    def save(self, *args, **kwargs):
        # Si hay fecha programada y el estado aún no está ejecutado
        if self.fechaEjecutada:
            self.estado = TipoEstado.REALIZADO
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre