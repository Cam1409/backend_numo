from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from apps.categories.views import CategoriUsuarioViewset, CategoriaViewset
from apps.users.views import UsuarioViewSet, login_usuario, registrar_usuario
from apps.frequency.views import (
    listar_frecuencias,
    set_frecuencia_fija,
    mi_frecuencia_fija,
)
from apps.incomes.views import ingresos_fijos, ingreso_fijo_detalle

router = routers.DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuarios')
router.register(r'categorias', CategoriaViewset, basename='categorias')
router.register(r'categoriasUsuario', CategoriUsuarioViewset, basename='categoriasUsuario')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),

    # usuarios
    path('api/registrar/', registrar_usuario, name='registrar_usuario'),
    path('api/login/', login_usuario, name='login_usuario'),

    # frequency
    path('frecuencias/', listar_frecuencias),          # GET
    path('frecuencia-fija/', set_frecuencia_fija),     # POST/PUT  (requiere auth)
    path('frecuencia-fija/mia/', mi_frecuencia_fija),  # GET       (requiere auth)

    # incomes
    path('api/ingresos-fijos/', ingresos_fijos),                          # GET/POST
    path('api/ingresos-fijos/<uuid:ingreso_id>/', ingreso_fijo_detalle),  # GET/PATCH/DELETE
]

