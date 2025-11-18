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
from apps.goals.views import ObjetivoViewset, DetalleObjetivoViewset
from apps.rules.views import ReglaViewset, ReglaDetalleViewset
from apps.tarea.views import TareaViewset
from apps.users.views import (
    enviar_codigo_reset,
    verificar_codigo_reset,
    actualizar_password
)

router = routers.DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuarios')
router.register(r'categorias', CategoriaViewset, basename='categorias')
router.register(r'categoriasUsuario', CategoriUsuarioViewset, basename='categoriasUsuario')
router.register(r'objetivos', ObjetivoViewset, basename='objetivos')
router.register(r'detalles-objetivo', DetalleObjetivoViewset, basename='detalles-objetivo')
router.register(r'reglas', ReglaViewset, basename='reglas')
router.register(r'reglas-detalle', ReglaDetalleViewset, basename='reglas-detalle')
router.register(r'tarea', TareaViewset, basename="tarea")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),

    path('api/registrar/', registrar_usuario, name='registrar_usuario'),
    path('api/login/', login_usuario, name='login_usuario'),

    path('frecuencias/', listar_frecuencias),         
    path('frecuencia-fija/', set_frecuencia_fija),     
    path('frecuencia-fija/mia/', mi_frecuencia_fija),  
   
    path('api/reset/enviar-codigo/', enviar_codigo_reset, name='enviar_codigo_reset'),
    path('api/reset/verificar-codigo/', verificar_codigo_reset, name='verificar_codigo_reset'),
    path('api/reset/actualizar-password/', actualizar_password, name='actualizar_password'),
]

