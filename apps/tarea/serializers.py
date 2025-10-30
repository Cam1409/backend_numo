from rest_framework import serializers
from apps.tarea.models import Tarea

class TareaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarea
        fields = '__all__'
        read_only_fields = ['usuario']  # Para prevenir que el usuario lo modifique
