from django.contrib.auth.hashers import check_password, make_password
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password

from apps.users.models import Usuario, Credencial  # ajusta import
from apps.users.serializers import UsuarioSerializer
from wapp.jwt_utils import make_access_token, make_refresh_token  # ajusta import

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]

@api_view(['POST'])
def login_usuario(request):
    email = request.data.get('email')
    password = request.data.get('password')
    print(request)

    if not email or not password:
        print('1')
        return Response({'error': 'Faltan credenciales.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        print('2')
        usuario = Usuario.objects.get(correo=email)
    except Usuario.DoesNotExist:
        return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    try:
        print('3')
        credencial = Credencial.objects.get(usuario=usuario)
    except Credencial.DoesNotExist:
        return Response({'error': 'Credencial no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

    # hash_password es BinaryField => decodificamos a str para check_password
    hashed = credencial.hash_password.decode() if isinstance(credencial.hash_password, (bytes, bytearray)) else credencial.hash_password

    if not check_password(password, hashed):
        return Response({'error': 'Contraseña incorrecta.'}, status=status.HTTP_401_UNAUTHORIZED)

    # ✅ Credenciales correctas -> emitir JWT
    access = make_access_token(usuario.id, usuario.correo)
    refresh = make_refresh_token(usuario.id)

    data = UsuarioSerializer(usuario).data
    # Opción A: devolver en cuerpo (Bearer en header del cliente)
    return Response(
        {
            'usuario': data,
            'access': access,
            'refresh': refresh
        },
        status=status.HTTP_200_OK
    )


#Endpoint para crear un usario 

@api_view(['POST'])
def registrar_usuario(request):
    nombre = request.data.get('nombre', '').strip()
    apellido = request.data.get('apellido', '').strip()
    dni = request.data.get('dni', '').strip()
    numero_tel = request.data.get('numero_tel', '').strip()
    correo = request.data.get('correo', '').strip().lower()
    password = request.data.get('password', '')

    if not (nombre and apellido and dni and numero_tel and correo and password):
        return Response({'error': 'Faltan campos.'}, status=status.HTTP_400_BAD_REQUEST)

    # valida unicidad del correo
    if Usuario.objects.filter(correo=correo).exists():
        return Response({'error': 'El correo ya está registrado.'}, status=status.HTTP_400_BAD_REQUEST)

    # crea usuario
    usuario = Usuario.objects.create(
        nombre=nombre,
        apellido=apellido,
        dni=dni,
        numero_tel=numero_tel,
        correo=correo,
    )

    # hashea y guarda credencial (tu modelo usa BinaryField)
    hashed = make_password(password)  # str
    Credencial.objects.create(
        usuario=usuario,
        email_login=correo,
        hash_password=hashed.encode('utf-8'),  # -> bytes
        salt=b'',
    )

    data = UsuarioSerializer(usuario).data
    return Response({'usuario': data}, status=status.HTTP_201_CREATED)