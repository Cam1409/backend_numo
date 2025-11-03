from django.contrib import admin
from .models import Objetivo


class ObjetivoAdmin(admin.ModelAdmin):
    list_display = (
        "usuario",
        "nombre",
    )
    list_filter= ["usuario"]

admin.site.register(Objetivo, ObjetivoAdmin)
