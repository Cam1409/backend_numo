# apps/users/serializers.py
from rest_framework import serializers
from .models import Usuario, Credencial


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'


class CredencialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Credencial
        exclude = ('hash_password', 'salt')  # ocultamos campos sensibles
