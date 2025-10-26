from django.contrib import admin
from .models import Frecuencia, FrecuenciaFija

@admin.register(Frecuencia)
class FrecuenciaAdmin(admin.ModelAdmin):
    list_display = ('descripcion',)
    search_fields = ('descripcion',)  # ← REQUERIDO

@admin.register(FrecuenciaFija)
class FrecuenciaFijaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'frecuencia', 'created_at')
    search_fields = ('usuario__nombre', 'usuario__apellido', 'frecuencia__descripcion')
    autocomplete_fields = ('usuario', 'frecuencia')
