from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import IngresoFijo
from .serializers import IngresoFijoSerializer

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def ingresos_fijos(request):
    print(request)
    if request.method == 'GET':
        qs = IngresoFijo.objects.filter(usuario=request.user, activo=True) \
                                .order_by('-es_principal','-created_at')
        return Response(IngresoFijoSerializer(qs, many=True).data)

    data = request.data.copy()
    data['usuario'] = request.user.id
    ser = IngresoFijoSerializer(data=data)
    if ser.is_valid():
        ser.save(usuario=request.user)
        return Response(ser.data, status=status.HTTP_201_CREATED)
    return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT','PATCH','DELETE','GET'])
@permission_classes([IsAuthenticated])
def ingreso_fijo_detalle(request, ingreso_id):
    try:
        obj = IngresoFijo.objects.get(id_ingreso_fijo=ingreso_id, usuario=request.user)
    except IngresoFijo.DoesNotExist:
        return Response({'detail':'No encontrado'}, status=404)

    if request.method == 'GET':
        return Response(IngresoFijoSerializer(obj).data)

    if request.method in ['PUT','PATCH']:
        ser = IngresoFijoSerializer(obj, data=request.data, partial=True)
        if ser.is_valid():
            ser.save()
            return Response(ser.data)
        return Response(ser.errors, status=400)

    # DELETE lógico
    obj.activo = False
    obj.save()
    return Response(status=204)
