from django.contrib import admin
from .models import Categoria, CategoriUsuario

class CategoriUsuarioAdmin(admin.ModelAdmin):
    list_display = ("usuario", "categoria",  "descripcion")
    list_filter = ["usuario"]
admin.site.register(Categoria)
admin.site.register(CategoriUsuario, CategoriUsuarioAdmin)



