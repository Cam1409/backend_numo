import jwt
from datetime import datetime, timezone
from django.conf import settings
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework import exceptions
from apps.users.models import Usuario  # ajusta import

class JWTAuthentication(BaseAuthentication):
    keyword = b"Bearer"

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower():
            return None  # sin header -> DRF probará otras auth classes o negará acceso

        if len(auth) != 2:
            raise exceptions.AuthenticationFailed("Cabecera Authorization inválida.")

        token = auth[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Token expirado.")
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed("Token inválido.")

        user_id = payload.get("sub")
        if not user_id:
            raise exceptions.AuthenticationFailed("Token sin sujeto.")

        try:
            usuario = Usuario.objects.get(id_usuario=user_id)

        except Usuario.DoesNotExist:
            raise exceptions.AuthenticationFailed("Usuario no existe.")

        # Retornar (user, auth) — para DRF, el segundo valor puede ser None
        return (usuario, None)
