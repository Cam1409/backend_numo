from django.contrib import admin
from .models import Objetivo


class ObjetivoAdmin(admin.ModelAdmin):
    list_display = (
        "usuario",
        "nombre",
    )


admin.site.register(Objetivo, ObjetivoAdmin)
