from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from django.contrib.auth.hashers import check_password, make_password

from apps.users.models import Usuario, Credencial
from apps.users.serializers import UsuarioSerializer
from wapp.jwt_utils import make_access_token, make_refresh_token
from rest_framework.decorators import api_view, permission_classes


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [AllowAny]


@api_view(['POST'])
@permission_classes([AllowAny])
def login_usuario(request):
    email = request.data.get('email')
    password = request.data.get('password')
    print(request.data)

    if not email or not password:
        return Response({'error': 'Faltan credenciales.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        usuario = Usuario.objects.get(correo=email)
    except Usuario.DoesNotExist:
        return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    try:
        credencial = Credencial.objects.get(usuario=usuario)
    except Credencial.DoesNotExist:
        return Response({'error': 'Credencial no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

    hashed = (
        credencial.hash_password.decode()
        if isinstance(credencial.hash_password, (bytes, bytearray))
        else credencial.hash_password
    )

    if not check_password(password, hashed):
        return Response({'error': 'Contraseña incorrecta.'}, status=status.HTTP_401_UNAUTHORIZED)

    access = make_access_token(str(usuario.id_usuario), usuario.correo)
    refresh = make_refresh_token(str(usuario.id_usuario))


    #data = UsuarioSerializer(usuario).data

    return Response(
        {
            #'usuario': data,
            'access': access,
            'refresh': refresh,
        },
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def registrar_usuario(request):
    """
    Crea un nuevo usuario y su credencial asociada.
    """
    campos = ['nombre', 'apellido', 'dni', 'numero_tel', 'correo', 'password']
    datos = {campo: request.data.get(campo, '').strip() for campo in campos}

    if not all(datos.values()):
        return Response({'error': 'Faltan campos.'}, status=status.HTTP_400_BAD_REQUEST)

    correo = datos['correo'].lower()

    if Usuario.objects.filter(correo=correo).exists():
        return Response({'error': 'El correo ya está registrado.'}, status=status.HTTP_400_BAD_REQUEST)

    usuario = Usuario.objects.create(
        nombre=datos['nombre'],
        apellido=datos['apellido'],
        dni=datos['dni'],
        numero_tel=datos['numero_tel'],
        correo=correo,
    )

    hashed_password = make_password(datos['password'])

    Credencial.objects.create(
        usuario=usuario,
        email_login=correo,
        hash_password=hashed_password, 
        salt=b'',  
    )

    return Response(status=status.HTTP_201_CREATED)
