from rest_framework import viewsets, status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q

from .models import Regla, ReglaDetalle
from .serializers import ReglaSerializer, ReglaDetalleSerializer


class ReglaViewset(viewsets.ModelViewSet):
    """
    CRUD de Regla. Filtros:
      - ?activa=true/false
    Búsqueda:
      - ?search=<texto> (sobre descripcion)
    """
    queryset = Regla.objects.all().order_by('-id_regla')
    serializer_class = ReglaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['descripcion']

    def get_queryset(self):
        qs = super().get_queryset()
        activa = self.request.query_params.get('activa')
        if activa is not None:
            if activa.lower() in ('true', '1'):
                qs = qs.filter(activa=True)
            elif activa.lower() in ('false', '0'):
                qs = qs.filter(activa=False)
        return qs


class ReglaDetalleViewset(viewsets.ModelViewSet):
    """
    CRUD de ReglaDetalle.
    - List: por defecto solo las del usuario autenticado.
      * ?include_global=true para incluir registros con usuario=None.
      * ?regla=<uuid> para filtrar por una regla.
      * ?activa=true/false
    - Create: asigna usuario desde el token automáticamente.
    """
    serializer_class = ReglaDetalleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = getattr(self.request, 'user', None)
        if not (user and hasattr(user, 'id_usuario')):
            return ReglaDetalle.objects.none()

        qs = ReglaDetalle.objects.filter(usuario=user)

        # incluir globales (usuario=None) si se pide
        include_global = self.request.query_params.get('include_global')
        if include_global and include_global.lower() in ('true', '1'):
            qs = ReglaDetalle.objects.filter(Q(usuario=user) | Q(usuario__isnull=True))

        # filtro por regla
        regla_id = self.request.query_params.get('regla')
        if regla_id:
            qs = qs.filter(regla_id=regla_id)

        # filtro por activa
        activa = self.request.query_params.get('activa')
        if activa is not None:
            if activa.lower() in ('true', '1'):
                qs = qs.filter(activa=True)
            elif activa.lower() in ('false', '0'):
                qs = qs.filter(activa=False)

        return qs.order_by('-id_regla_detalle')

    def create(self, request, *args, **kwargs):
        usuario = getattr(request, 'user', None)
        if not (usuario and hasattr(usuario, 'id_usuario')):
            return Response({'error': 'No autorizado.'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(usuario=usuario)  # asigna usuario del token
        return Response(self.get_serializer(instance).data, status=status.HTTP_201_CREATED)
