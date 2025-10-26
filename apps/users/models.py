from django.db import models
import uuid
from django.contrib.auth.hashers import check_password, make_password

class Usuario(models.Model):
    id_usuario   = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dni          = models.CharField(max_length=8, unique=True)
    nombre       = models.CharField(max_length=100)
    apellido     = models.CharField(max_length=100)
    numero_tel   = models.CharField(max_length=15)
    correo       = models.EmailField(unique=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)  # ok si la tabla aún no existe
    activo       = models.BooleanField(default=True)

    class Meta:
        db_table = 'Usuario'

    def __str__(self):
        return f'{self.nombre} {self.apellido}'

class Credencial(models.Model):
    id_credencial = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # misma app => nombre simple
    usuario       = models.OneToOneField('Usuario', on_delete=models.CASCADE, related_name='credencial')
    email_login   = models.EmailField(max_length=150, unique=True)
    hash_password = models.BinaryField(max_length=512)
    salt          = models.BinaryField(max_length=128)
    ultimo_acceso = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if isinstance(self.hash_password, str):
            self.hash_password = make_password(self.hash_password).encode()
        super().save(*args, **kwargs)
        
    class Meta:
        db_table = 'Credencial'

