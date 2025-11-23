# apps/users/email_utils.py

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings


def enviar_correo_reset(correo_destino: str, codigo: str) -> bool:
    """
    Envía el correo de recuperación de contraseña usando la API HTTP de SendGrid.

    :param correo_destino: Email del usuario que solicitó el cambio de contraseña.
    :param codigo: Código de 6 dígitos generado para el reset.
    :return: True si se envió correctamente, False si hubo algún error.
    """
    # Construimos el correo
    message = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=correo_destino,
        subject="Código de recuperación de contraseña",
        plain_text_content=f"Tu código de recuperación es: {codigo}",
    )

    try:
        api_key = os.getenv("SENDGRID_API_KEY")
        if not api_key:
            print("SENDGRID_API_KEY no está configurada en el entorno.")
            return False

        sg = SendGridAPIClient(api_key)
        response = sg.send(message)

        # Para ver en los logs qué está respondiendo SendGrid
        print("SendGrid status:", response.status_code)
        print("SendGrid body:", response.body)
        print("SendGrid headers:", response.headers)

        # Consideramos éxito cualquier 2xx
        return 200 <= response.status_code < 300

    except Exception as e:
        # Esto aparecerá en los logs de Render si hay problema
        print("Error enviando correo con SendGrid:", repr(e))
        return False
