from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from apps.categories.models import CategoriUsuario, Categoria
from apps.categories.serializers import CategoriUsuarioSerializer, CategoriaSerializer, ResumenSemanalSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
from rest_framework.response import Response

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
        Crea una categoría de usuario tomando el usuario autenticado del token.
        """
        usuario = request.user  # viene del token JWT (DRF decodifica automáticamente)
        print(usuario)

        # 🔒 Verifica que el usuario venga autenticado
        if not usuario :
            return Response({'error': 'No autorizado.'}, status=status.HTTP_401_UNAUTHORIZED)

        # 👇 Crea el objeto usando los datos del request y el usuario del token
        data = request.data.copy()
        data['usuario'] = usuario.id_usuario  # inyectamos el id del usuario autenticado

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
