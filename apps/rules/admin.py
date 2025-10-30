from django.contrib import admin
from .models import Regla, ReglaDetalle


class ReglaDetalleAdmin(admin.ModelAdmin):
    list_display = (
        "regla",
        "usuario",

    ) 
    list_filter=("usuario",)



admin.site.register(Regla)
admin.site.register(ReglaDetalle, ReglaDetalleAdmin)
