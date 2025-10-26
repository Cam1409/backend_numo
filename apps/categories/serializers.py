from apps.categories.models import CategoriUsuario, Categoria
from rest_framework import serializers

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria 
        fields = "__all__"

class CategoriUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriUsuario 
        fields = "__all__"