from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

from .models import Frecuencia, FrecuenciaFija
from .serializers import FrecuenciaSerializer, FrecuenciaFijaSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def listar_frecuencias(request):
    qs = Frecuencia.objects.order_by('descripcion')
    return Response(FrecuenciaSerializer(qs, many=True).data)


@api_view(['POST', 'PUT'])
@permission_classes([IsAuthenticated])
def set_frecuencia_fija(request):
    """
    Crea o actualiza la frecuencia fija del usuario autenticado.
    Body:
      - frecuencia_id (uuid)  O  frecuencia (texto: DIARIO/SEMANAL/QUINCENAL/MENSUAL)
    """
    freq = None
    freq_id = request.data.get('frecuencia_id')
    freq_txt = request.data.get('frecuencia')

    if freq_id:
        freq = Frecuencia.objects.filter(id_frecuencia=freq_id).first()
    elif freq_txt:
        freq = Frecuencia.objects.filter(descripcion=freq_txt.strip().upper()).first()

    if not freq:
        return Response({"error": "Frecuencia inválida."}, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        obj, created = FrecuenciaFija.objects.update_or_create(
            usuario=request.user,
            defaults={'frecuencia': freq}
        )

    return Response(
        FrecuenciaFijaSerializer(obj).data,
        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mi_frecuencia_fija(request):
    obj = FrecuenciaFija.objects.filter(usuario=request.user).first()
    if not obj:
        return Response({"detail": "Sin frecuencia fija aún."}, status=status.HTTP_404_NOT_FOUND)
    return Response(FrecuenciaFijaSerializer(obj).data)
