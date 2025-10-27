from django.shortcuts import render
from rest_framework import viewsets

from apps.categories.models import CategoriUsuario, Categoria
from apps.categories.serializers import CategoriUsuarioSerializer, CategoriaSerializer
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
