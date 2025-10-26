from django.contrib import admin
from .models import IngresoFijo

@admin.register(IngresoFijo)
class IngresoFijoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'usuario', 'monto', 'frecuencia', 'es_principal', 'activo', 'created_at')
    list_filter  = ('activo', 'es_principal', 'frecuencia')
    search_fields = ('nombre', 'usuario__nombre', 'usuario__apellido', 'usuario__correo')
    autocomplete_fields = ('usuario', 'frecuencia')
    ordering = ('-created_at',)

