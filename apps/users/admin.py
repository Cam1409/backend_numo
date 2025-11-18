from django.contrib import admin
from .models import Usuario, Credencial

class CredencialInline(admin.StackedInline):
    model = Credencial
    fk_name = 'usuario'
    can_delete = False
    extra = 0

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'dni','correo', 'activo')
    search_fields = ('nombre', 'apellido', 'correo', 'dni')  # ← REQUERIDO
    inlines = [CredencialInline]

@admin.register(Credencial)
class CredencialAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'email_login', 'ultimo_acceso')
    search_fields = ('usuario__nombre', 'usuario__apellido', 'usuario__correo', 'usuario__dni')
    autocomplete_fields = ('usuario',)
