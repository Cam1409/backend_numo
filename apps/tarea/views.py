from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.tarea.models import Tarea
from apps.tarea.serializers import TareaSerializer


class TareaViewset(viewsets.ModelViewSet):
    queryset = Tarea.objects.all()
    serializer_class = TareaSerializer
    permission_classes = [IsAuthenticated]  # Requiere token

    def get_queryset(self):
        """
        Retorna solo las tareas del usuario autenticado.
        Permite filtrar por estado: ?estado=PENDIENTE
        """
        usuario = self.request.user
        queryset = Tarea.objects.filter(usuario=usuario.id_usuario)

        estado = self.request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)

        return queryset

    def create(self, request, *args, **kwargs):
        """
        Crea una tarea asignando el usuario autenticado desde el token.
        """
        usuario = request.user

        if not usuario:
            return Response({'error': 'No autorizado.'}, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data.copy()
        data['usuario'] = usuario.id_usuario  # inyectamos el usuario automáticamente

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

