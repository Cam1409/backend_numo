from rest_framework.decorators import api_view, authentication_classes
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
import random
from apps.users.models import CodigoRecuperacion, PasswordResetCode
from django.utils import timezone
from datetime import timedelta

from apps.users.email_utils import enviar_correo_reset


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

    hashed = credencial.hash_password

    if not check_password(password, hashed):
        return Response({'error': 'Contraseña incorrecta.'}, status=status.HTTP_401_UNAUTHORIZED)

    access = make_access_token(str(usuario.id_usuario), usuario.correo, usuario.nombre)
    refresh = make_refresh_token(str(usuario.id_usuario))

    return Response(
        {
            'access': access,
            'refresh': refresh,
            'message': 'Login exitoso.'
        },
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
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

@api_view(['POST'])
@permission_classes([AllowAny])
def enviar_codigo_recuperacion(request):
    email = (request.data.get("email") or "").strip().lower()

    if not email:
        return Response({"error": "Debe ingresar un correo"}, status=400)

    try:
        usuario = Usuario.objects.get(correo=email)
    except Usuario.DoesNotExist:
        return Response({"error": "El correo no está registrado."}, status=404)

    # Generar código de 6 dígitos
    codigo = str(random.randint(100000, 999999))

    # Guardar en BD
    CodigoRecuperacion.objects.create(usuario=usuario, codigo=codigo)

    # Enviar correo con SendGrid
    ok = enviar_correo_reset(email, codigo)

    if not ok:
        return Response(
            {"error": "No se pudo enviar el correo de recuperación."},
            status=500
        )

    return Response({"message": "Código enviado correctamente."}, status=200)

@api_view(['POST'])
@permission_classes([AllowAny])
def verificar_codigo_recuperacion(request):
    email = (request.data.get("email") or "").strip().lower()
    codigo = (request.data.get("codigo") or "").strip()

    try:
        usuario = Usuario.objects.get(correo=email)
    except Usuario.DoesNotExist:
        return Response({"error": "Correo no válido."}, status=404)

    try:
        registro = CodigoRecuperacion.objects.filter(
            usuario=usuario,
            codigo=codigo,
            usado=False
        ).latest('creado')
    except CodigoRecuperacion.DoesNotExist:
        return Response({"error": "Código incorrecto."}, status=400)

    # Verificar expiración
    if timezone.now() > registro.expiracion:
        return Response({"error": "El código expiró."}, status=400)

    # Marcar como usado
    registro.usado = True
    registro.save()

    return Response({"message": "Código verificado correctamente."}, status=200)
@api_view(['POST'])
@permission_classes([AllowAny])
def actualizar_password(request):
    email = (request.data.get("email") or "").strip().lower()
    new_password = (request.data.get("password") or "")

    if len(new_password) < 8:
        return Response({"error": "La contraseña debe tener mínimo 8 caracteres."}, status=400)

    try:
        usuario = Usuario.objects.get(correo=email)
        credencial = Credencial.objects.get(usuario=usuario)
    except:
        return Response({"error": "Correo no válido."}, status=404)

    # Reemplazar contraseña
    hashed = make_password(new_password)
    credencial.hash_password = hashed.encode()
    credencial.save()

    return Response({"message": "Contraseña actualizada correctamente."}, status=200)
@api_view(['POST'])
@permission_classes([AllowAny])
def enviar_codigo_reset(request):
    email = (request.data.get("correo") or "").strip().lower()

    if not email:
        return Response({"error": "El correo es obligatorio."}, status=400)

    try:
        usuario = Usuario.objects.get(correo=email)
    except Usuario.DoesNotExist:
        return Response({"error": "El correo no está registrado."}, status=404)

    # Crear código de 6 dígitos
    codigo = str(random.randint(100000, 999999))

    # Guardar el código en la BD
    PasswordResetCode.objects.create(usuario=usuario, codigo=codigo)

    # 🔹 Enviar correo con SendGrid (API HTTP)
    ok = enviar_correo_reset(email, codigo)

    if not ok:
        return Response(
            {"error": "No se pudo enviar el correo de recuperación."},
            status=500
        )

    return Response({"message": "Código enviado al correo."}, status=200)

@api_view(['POST'])
@permission_classes([AllowAny])
def verificar_codigo_reset(request):
    email = (request.data.get("correo") or "").strip().lower()
    codigo = (request.data.get("codigo") or "").strip()

    try:
        usuario = Usuario.objects.get(correo=email)
    except Usuario.DoesNotExist:
        return Response({"error": "Correo no válido."}, status=404)

    # buscar un código válido (no usado y menos de 10 min)
    limite = timezone.now() - timedelta(minutes=10)

    try:
        reset = PasswordResetCode.objects.filter(
            usuario=usuario,
            codigo=codigo,
            usado=False,
            creado_en__gte=limite
        ).latest("creado_en")
    except PasswordResetCode.DoesNotExist:
        return Response({"error": "Código incorrecto o expirado."}, status=400)

    return Response({"message": "Código correcto."}, status=200)
@api_view(['POST'])
@permission_classes([AllowAny])
def actualizar_password(request):
    email = (request.data.get("correo") or "").strip().lower()
    codigo = (request.data.get("codigo") or "").strip()
    nueva_password = request.data.get("password")

    if not nueva_password:
        return Response({"error": "Debe ingresar una nueva contraseña."}, status=400)

    try:
        usuario = Usuario.objects.get(correo=email)
    except Usuario.DoesNotExist:
        return Response({"error": "Correo no válido."}, status=404)

    limite = timezone.now() - timedelta(minutes=10)

    try:
        reset = PasswordResetCode.objects.filter(
            usuario=usuario,
            codigo=codigo,
            usado=False,
            creado_en__gte=limite
        ).latest("creado_en")
    except PasswordResetCode.DoesNotExist:
        return Response({"error": "Código incorrecto o expirado."}, status=400)

    # actualizar contraseña
    cred = Credencial.objects.get(usuario=usuario)
    cred.hash_password = make_password(nueva_password)
    cred.save()

    reset.usado = True
    reset.save()

    return Response({"message": "Contraseña actualizada correctamente."}, status=200)
