from django.contrib import admin
from .models import Categoria, CategoriUsuario

class CategoriUsuarioAdmin(admin.ModelAdmin):
    list_display = ("usuario", "categoria", )
admin.site.register(Categoria)
admin.site.register(CategoriUsuario, CategoriUsuarioAdmin)



