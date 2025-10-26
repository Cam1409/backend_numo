from rest_framework import serializers
from .models import IngresoFijo

class IngresoFijoSerializer(serializers.ModelSerializer):
    frecuencia_descripcion = serializers.ReadOnlyField(source='frecuencia.descripcion')
    monto_mensual_equivalente = serializers.SerializerMethodField()

    class Meta:
        model = IngresoFijo
        fields = ('id_ingreso_fijo','usuario','nombre','monto','frecuencia',
                  'frecuencia_descripcion','fecha_inicio','dia_corte',
                  'es_principal','activo','monto_mensual_equivalente',
                  'created_at','updated_at')
        read_only_fields = ('usuario','created_at','updated_at')

    def get_monto_mensual_equivalente(self, obj):
        return str(obj.monto_mensual_equivalente)
