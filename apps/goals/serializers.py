from rest_framework import serializers
from .models import Objetivo, DetalleObjetivo

class ObjetivoSerializer(serializers.ModelSerializer):
    usuario = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Objetivo
        fields = '__all__'
        read_only_fields = ('usuario',)

class DetalleObjetivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleObjetivo
        fields = '__all__'
