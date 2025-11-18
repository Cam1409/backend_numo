from django.db import models
import uuid
from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone
from datetime import timedelta

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
        ordering = ["-fecha_registro"]

    def __str__(self):
        return f'{self.nombre} {self.apellido}'
    
    @property
    def is_authenticated(self):
        return True

class Credencial(models.Model):
    id_credencial = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario       = models.OneToOneField('Usuario', on_delete=models.CASCADE, related_name='credencial')
    email_login   = models.EmailField(max_length=150, unique=True)
    hash_password = models.CharField(max_length=512)
    salt          = models.BinaryField(max_length=128)
    ultimo_acceso = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if isinstance(self.hash_password, str) and not self.hash_password.startswith("pbkdf2_"):
            self.hash_password = make_password(self.hash_password)
        super().save(*args, **kwargs)
        
    class Meta:
        db_table = 'Credencial'

class CodigoRecuperacion(models.Model):
    id_codigo = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="codigos_recuperacion")

    codigo = models.CharField(max_length=6)
    creado = models.DateTimeField(default=timezone.now)
    expiracion = models.DateTimeField()
    usado = models.BooleanField(default=False)

    class Meta:
        db_table = "CodigoRecuperacion"

    def save(self, *args, **kwargs):
        if not self.expiracion:
            self.expiracion = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)

class PasswordResetCode(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    codigo = models.CharField(max_length=6)
    creado_en = models.DateTimeField(auto_now_add=True)
    usado = models.BooleanField(default=False)

    class Meta:
        db_table = 'PasswordResetCode'
