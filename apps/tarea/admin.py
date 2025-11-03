from django.contrib import admin
from .models import Tarea

class TareaU(admin.ModelAdmin):
    list_display=("usuario", "nombre", "fechaProgramada", "fechaEjecutada")
    list_filter= ["usuario"]

admin.site.register(Tarea, TareaU)
