from django.contrib import admin
from .models import Categoria, CategoriUsuario

class CategoriUsuarioAdmin(admin.ModelAdmin):
    list_display = ("usuario", "categoria",  "descripcion")
    list_filter = ["usuario"]

class CategoriaAdmin(admin.ModelAdmin):
    # Campos que se mostrarán en la tabla del admin
    list_display = ("nombre","descripcion", "tipo_categoria")

    
admin.site.register(CategoriUsuario, CategoriUsuarioAdmin)
admin.site.register(Categoria, CategoriaAdmin)


