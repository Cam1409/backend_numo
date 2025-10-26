from django.shortcuts import render
from rest_framework import viewsets

from apps.categories.models import CategoriUsuario, Categoria
from apps.categories.serializers import CategoriUsuarioSerializer, CategoriaSerializer

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

