from django.contrib import admin
from .models import PorcentajeEjecucion, ControlConsumo

class PlanificacionPresupuestaria(admin.ModelAdmin):
    list_display=("usuario", "montoEjecutado",
                  "montoPlanificado", "porcentaje")
    list_filter= ["usuario"]

class ControlDelConsumo (admin.ModelAdmin):
    list_display= ("usuario", "n_ajustesPresupuestales",
                   "tareasRealizadasEnFecha", "totalTareasProgramadas",
                   "porcentaje")
    list_filter= ["usuario"]
                   

admin.site.register(PorcentajeEjecucion,PlanificacionPresupuestaria)
admin.site.register(ControlConsumo, ControlDelConsumo)
