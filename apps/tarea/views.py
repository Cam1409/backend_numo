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
        print('entre')
        usuario = self.request.user
        queryset = Tarea.objects.filter(usuario=usuario.id_usuario)
        print(usuario.id_usuario)
        print(queryset)

        estado = self.request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)

        return queryset
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # ✅ Asigna usuario en save (no en data)
        instance = serializer.save(usuario_id=request.user.id_usuario)

        # ✅ Re-serializa la instancia para asegurar que venga 'usuario'
        out = self.get_serializer(instance)
        return Response(out.data, status=status.HTTP_201_CREATED)


