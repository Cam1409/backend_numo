# apps/users/serializers.py
from rest_framework import serializers
from .models import Usuario, Credencial


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'

    def update(self, instance, validated_data):
        """
        Permite actualizar los datos del usuario autenticado.
        Solo se actualizan los campos enviados en la petición.
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class CredencialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Credencial
        exclude = ('hash_password', 'salt')  # ocultamos campos sensibles
