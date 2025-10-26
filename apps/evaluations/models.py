from django.db import models
import uuid

class Evaluacion(models.Model):
    class Tipo(models.TextChoices):
        PRE  = 'PRE', 'Pre'
        POST = 'POST', 'Post'

    class Fuente(models.TextChoices):
        DECLARADA = 'DECLARADA', 'Declarada'
        CALCULADA = 'CALCULADA', 'Calculada'

    id_evaluacion = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey('users.Usuario', on_delete=models.CASCADE, related_name='evaluaciones')
    periodo = models.ForeignKey('period.Periodo', on_delete=models.PROTECT, related_name='evaluaciones')
    tipo = models.CharField(max_length=10, choices=Tipo.choices)
    fuente = models.CharField(max_length=15, choices=Fuente.choices)
    capturado_en = models.DateTimeField(auto_now_add=True)
    observacion = models.CharField(max_length=250, null=True, blank=True)

    class Meta:
        db_table = 'Evaluacion'
        unique_together = (('usuario', 'periodo', 'tipo'),)

    def __str__(self):
        return f'{self.usuario_id}-{self.periodo_id}-{self.tipo}'

class Metrica(models.Model):
    id_metrica   = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo       = models.CharField(max_length=50, unique=True)
    descripcion  = models.CharField(max_length=200)
    unidad       = models.CharField(max_length=20)

    class Meta:
        db_table = 'Metrica'

    def __str__(self):
        return self.codigo

class EvaluacionMetrica(models.Model):
    id_eval_metrica = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    evaluacion = models.ForeignKey('evaluations.Evaluacion', on_delete=models.CASCADE, related_name='metricas')
    metrica    = models.ForeignKey('evaluations.Metrica', on_delete=models.PROTECT, related_name='evaluaciones')
    valor_numerico = models.DecimalField(max_digits=18, decimal_places=4)

    class Meta:
        db_table = 'EvaluacionMetrica'
        unique_together = (('evaluacion', 'metrica'),)
