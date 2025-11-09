from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from apps.categories.models import CategoriUsuario, Categoria
from apps.categories.serializers import CategoriUsuarioSerializer, CategoriaSerializer, ResumenSemanalSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
from rest_framework.response import Response
from apps.tarea.models import Tarea
from django.db import transaction
from datetime import date
from apps.tarea.choices import TipoEstado

class CategoriaViewset(viewsets.ModelViewSet):
    
    serializer_class = CategoriaSerializer


    def get_queryset(self):
        queryset = Categoria.objects.all() 
        tipo_categoria = self.request.query_params.get("tipo_categoria")
        if tipo_categoria: 
            queryset = queryset.filter(tipo_categoria = tipo_categoria)

        return queryset    

class CategoriUsuarioViewset(viewsets.ModelViewSet):
    queryset = CategoriUsuario.objects.all()
    serializer_class = CategoriUsuarioSerializer
    permission_classes = [IsAuthenticated]  # 👈 requiere token válido

    def get_queryset(self):
        """
        Filtra las categorías por el usuario autenticado y, opcionalmente, por tipo_categoria.
        """
        usuario = self.request.user
        queryset = CategoriUsuario.objects.filter(usuario=usuario.id_usuario)

        # 🧩 Si viene el parámetro ?tipo_categoria=INGRESO, filtra adicionalmente
        tipo_categoria = self.request.query_params.get('tipo_categoria')
        if tipo_categoria:
            queryset = queryset.filter(categoria__tipo_categoria=tipo_categoria)

        return queryset
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Asegura pertenencia y tipo
        if instance.usuario_id != request.user.id_usuario:
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        if instance.categoria and instance.categoria.tipo_categoria != 'Gasto_Fijo':
            return Response({'detail': 'Solo se permiten gastos fijos.'}, status=status.HTTP_400_BAD_REQUEST)
        return super().partial_update(request, *args, **kwargs)

    @action(detail=False, methods=["get"], url_path="resumen-semanal")
    def resumen_semanal(self, request):
        """Devuelve el resumen semanal del usuario autenticado."""
        usuario = request.user

        # Pasamos un objeto falso con atributo usuario, ya que el serializer lo espera como obj.usuario
        dummy_obj = type("obj", (), {"usuario": usuario})()

        serializer = ResumenSemanalSerializer(dummy_obj)
        data = {
            "total_gastos": serializer.get_total_gastos(dummy_obj),
            "dia_mayor_gasto": serializer.get_dia_mayor_gasto(dummy_obj),
            "ultimo_ingreso_semana": serializer.get_ultimo_ingreso_semana(dummy_obj),
            "dia_ultimo_ingreso": serializer.get_dia_ultimo_ingreso(dummy_obj),
            "categoria_mayor_gasto_dia": serializer.get_categoria_mayor_gasto_dia(dummy_obj),
            "categoria_menor_gasto_dia": serializer.get_categoria_menor_gasto_dia(dummy_obj),
            "ultimo_gasto_dia": serializer.get_ultimo_gasto_dia(dummy_obj),
            "ultimo_ingreso_dia": serializer.get_ultimo_ingreso_dia(dummy_obj),
            "gasto_categoria": serializer.get_gasto_categoria(dummy_obj)
        }

        return Response(data, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        """
        Crea una categoría de usuario con el usuario autenticado.
        Si el cuerpo trae 'tarea' o 'idTarea', se actualiza fechaEjecutada = hoy
        en la tarea que pertenezca al mismo usuario.
        """
        usuario = request.user
        if not usuario:
            return Response({'error': 'No autorizado.'}, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data.copy()
        data['usuario'] = usuario.id_usuario  # ✅ conserva la funcionalidad original

        # Tomamos el id de tarea si llega
        tarea_id = request.data.get('tarea') or request.data.get('idTarea')

        with transaction.atomic():
            # 1) Crear CategoriUsuario (funcionalidad original)
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()

            # 2) Si llegó tarea, actualizar fechaEjecutada = hoy
            if tarea_id:
                try:
                    # Asegurar que la tarea exista y sea del mismo usuario
                    tarea = (
                        Tarea.objects
                        .select_for_update()
                        .get(idTarea=tarea_id, usuario=usuario)
                    )
                    if not tarea.fechaEjecutada:
                        tarea.fechaEjecutada = date.today()
                        tarea.save(update_fields=['fechaEjecutada'])
                        tarea.estado=TipoEstado.REALIZADO
                        tarea.save(update_fields=['estado'])
                except Tarea.DoesNotExist:
                    return Response(
                        {'error': 'La tarea no existe o no pertenece al usuario autenticado.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

        return Response(serializer.data, status=status.HTTP_201_CREATED)