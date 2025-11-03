from django.db import models

class PorcentajeEjecucion(models.Model):
    usuario = models.ForeignKey(
        "users.Usuario", on_delete=models.CASCADE, null=True, blank=True
    )
    montoEjecutado = models.DecimalField(decimal_places=2, max_digits=9 ,null=True, blank=True)
    montoPlanificado = models.DecimalField(decimal_places=2,  max_digits=9 ,null=True, blank=True)
    porcentaje =  models.DecimalField(decimal_places=2,  max_digits=9 ,null=True, blank=True)

    class Meta:
        db_table = "PorcentajeEjecucion"

class ControlConsumo (models.Model):
    usuario = models.ForeignKey(
        "users.Usuario", on_delete=models.CASCADE, null=True, blank=True
    )
    n_ajustesPresupuestales = models.IntegerField(null=True, blank=True)
    tareasRealizadasEnFecha = models.IntegerField(null=True, blank=True)
    totalTareasProgramadas  = models.IntegerField(null=True, blank=True)
    porcentaje =  models.DecimalField(decimal_places=2,  max_digits=9 ,null=True, blank=True)

    class Meta:
        db_table = "ControlConsumo"