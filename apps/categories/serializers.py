from apps.categories.models import CategoriUsuario, Categoria
from rest_framework import serializers

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria 
        fields = "__all__"

class CategoriUsuarioSerializer(serializers.ModelSerializer):
    nombre_categoria = serializers.CharField(source='categoria.nombre', read_only=True)

    class Meta:
        model = CategoriUsuario 
        fields = "__all__"
    
    def get_nombre_categoria(self, obj):
        return obj.categoria.nombre if obj.categoria else None