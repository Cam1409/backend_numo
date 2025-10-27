from rest_framework import serializers
from .models import Regla, ReglaDetalle

class ReglaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Regla
        fields = '__all__'

class ReglaDetalleSerializer(serializers.ModelSerializer):
    # El usuario lo setea el backend
    usuario = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ReglaDetalle
        fields = '__all__'
        read_only_fields = ('usuario',)
