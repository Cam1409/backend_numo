from rest_framework import serializers
from .models import Regla, ReglaDetalle


class ReglaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Regla
        fields = "__all__"


class ReglaDetalleSerializer(serializers.ModelSerializer):

    usuario = serializers.PrimaryKeyRelatedField(read_only=True)
    nombre_regla = serializers.CharField(source="regla.descripcion", read_only=True)

    class Meta:
        model = ReglaDetalle
        fields = "__all__"
        read_only_fields = ("usuario",)
        extra_kwargs = {"nombre_regla": {"read_only": True}}
