from django.db import models
import uuid
from apps.categories.choices import TipoCategoriaChoices
from apps.frequency.models import Frecuencia


class Categoria(models.Model):
    id_categoria = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    tipo_categoria = models.CharField(
        max_length=150, choices=TipoCategoriaChoices.choices
    )
    nombre = models.CharField(max_length=80)
    descripcion = models.CharField(max_length=200, null=True, blank=True)
    frecuencia = models.ForeignKey(
        Frecuencia, on_delete=models.PROTECT, null=True, blank=True
    )

    class Meta:
        db_table = "Categoria"

    def __str__(self):
        return self.nombre


class CategoriUsuario(models.Model):
    id_categoriaU = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    usuario = models.ForeignKey(
        "users.Usuario", on_delete=models.CASCADE, null=True, blank=True
    )
    categoria = models.ForeignKey(
        Categoria, on_delete=models.CASCADE, null=True, blank=True
    )
    monto = models.FloatField(null=True, blank=True)
    descripcion = models.CharField(max_length=200, null=True, blank=True)
    fecha = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "CategoriUsuario"

    def __str__(self):
        return self.descripcion or f"Categoría {self.pk}"  
