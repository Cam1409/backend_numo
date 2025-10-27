from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils.dateparse import parse_date

from .models import Objetivo, DetalleObjetivo
from .serializers import ObjetivoSerializer, DetalleObjetivoSerializer


class ObjetivoViewset(viewsets.ModelViewSet):
    serializer_class = ObjetivoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = getattr(self.request, "user", None)
        qs = Objetivo.objects.none()
        if user and hasattr(user, "id_usuario"):
            qs = Objetivo.objects.filter(usuario=user)

            # --- Filtros opcionales por query params ---
            estado = self.request.query_params.get("estado")
            if estado:
                qs = qs.filter(estado=estado)

            fecha_desde = parse_date(self.request.query_params.get("fecha_desde") or "")
            fecha_hasta = parse_date(self.request.query_params.get("fecha_hasta") or "")
            if fecha_desde:
                qs = qs.filter(fecha_objetivo__gte=fecha_desde)
            if fecha_hasta:
                qs = qs.filter(fecha_objetivo__lte=fecha_hasta)

            qs = qs.order_by("-fecha_objetivo", "-id_objetivo")
        return qs

    def create(self, request, *args, **kwargs):
        usuario = getattr(request, "user", None)
        if not (usuario and hasattr(usuario, "id_usuario")):
            return Response({'error': 'No autorizado.'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(usuario=usuario)  # asigna el usuario del token
        return Response(self.get_serializer(instance).data, status=status.HTTP_201_CREATED)


class DetalleObjetivoViewset(viewsets.ModelViewSet):
    queryset = DetalleObjetivo.objects.all().order_by("-fecha", "-idDetObjt")
    serializer_class = DetalleObjetivoSerializer
    permission_classes = [IsAuthenticated]
