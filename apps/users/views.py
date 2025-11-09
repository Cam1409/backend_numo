from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from django.contrib.auth.hashers import check_password, make_password

from apps.users.models import Usuario, Credencial
from apps.users.serializers import UsuarioSerializer
from wapp.jwt_utils import make_access_token, make_refresh_token
from rest_framework.decorators import api_view, permission_classes
from django.db import transaction
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [AllowAny]
    

    # solo usuarios autenticados pueden acceder
    @action(detail=False, methods=['get', 'patch'], permission_classes=[IsAuthenticated])
    def me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        elif request.method == 'PATCH':
            serializer = self.get_serializer(request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_usuario(request):
    """
    Login con email y password. Devuelve tokens (access, refresh).
    """
    email = (request.data.get('email') or '').strip().lower()
    password = (request.data.get('password') or '').strip()
    print(email)
    print(password)
    if not email or not password:
        return Response({'error': 'Faltan credenciales.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        usuario = Usuario.objects.get(correo=email)
        print(usuario)
    except Usuario.DoesNotExist:
        return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    try:
        credencial = Credencial.objects.get(usuario=usuario)
        print(credencial)
    except Credencial.DoesNotExist:
        return Response({'error': 'Credencial no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

    hashed = credencial.hash_password

    if not check_password(password, hashed):
        return Response({'error': 'Contraseña incorrecta.'}, status=status.HTTP_401_UNAUTHORIZED)

    access = make_access_token(str(usuario.id_usuario), usuario.correo, usuario.nombre)
    refresh = make_refresh_token(str(usuario.id_usuario))

    # data = UsuarioSerializer(usuario).data  # si quieres enviar info del usuario
    return Response(
        {
            # 'usuario': data,
            'access': access,
            'refresh': refresh,
            'message': 'Login exitoso.'
        },
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([AllowAny])
@transaction.atomic
def registrar_usuario(request):
    """
    Registra usuario + credencial y retorna tokens como el login.
    """
    campos = ['nombre', 'apellido', 'dni', 'numero_tel', 'correo', 'password']
    datos = {c: (request.data.get(c) or '').strip() for c in campos}

    if not all(datos.values()):
        return Response({'error': 'Faltan campos.'}, status=status.HTTP_400_BAD_REQUEST)

    correo = datos['correo'].lower()

    if Usuario.objects.filter(correo=correo).exists():
        return Response({'error': 'El correo ya está registrado.'}, status=status.HTTP_400_BAD_REQUEST)

    # Crear usuario
    usuario = Usuario.objects.create(
        nombre=datos['nombre'],
        apellido=datos['apellido'],
        dni=datos['dni'],
        numero_tel=datos['numero_tel'],
        correo=correo,
    )

    # Crear credencial
    hashed_password = make_password(datos['password'])
    Credencial.objects.create(
        usuario=usuario,
        email_login=correo,
        hash_password=hashed_password,
        salt=b'',  # si no usas salt manual, puedes quitar este campo del modelo
    )

    # Generar y devolver tokens igual que en login
    access = make_access_token(str(usuario.id_usuario), usuario.correo, usuario.nombre)
    refresh = make_refresh_token(str(usuario.id_usuario))
    # data = UsuarioSerializer(usuario).data

    return Response(
        {
            # 'usuario': data,
            'access': access,
            'refresh': refresh,
            'message': 'Usuario registrado y sesión iniciada.'
        },
        status=status.HTTP_201_CREATED
    )

    