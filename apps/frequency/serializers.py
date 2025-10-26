from rest_framework import serializers
from .models import Frecuencia, FrecuenciaFija

class FrecuenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Frecuencia
        fields = ('id_frecuencia', 'descripcion')

class FrecuenciaFijaSerializer(serializers.ModelSerializer):
    frecuencia_descripcion = serializers.ReadOnlyField(source='frecuencia.descripcion')

    class Meta:
        model = FrecuenciaFija
        fields = ('id_frecuencia_fija', 'usuario', 'frecuencia',
                  'frecuencia_descripcion', 'created_at', 'updated_at')

