import jwt
from datetime import datetime, timedelta, timezone
from django.conf import settings

def make_access_token(user_id: int, email: str, name: str) -> str:
    exp_minutes = getattr(settings, "JWT_ACCESS_MINUTES", 1440)
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "email": email,
        "name": name,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=exp_minutes)).timestamp()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

def make_refresh_token(user_id: int) -> str:
    days = getattr(settings, "JWT_REFRESH_DAYS", 7)
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=days)).timestamp()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
