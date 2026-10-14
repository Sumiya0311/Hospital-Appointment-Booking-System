from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt

from app.config import settings


def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["type"] = "access"
    payload["exp"] = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return jwt.encode(
        payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )


def create_refresh_token(data: dict) -> str:
    payload = data.copy()
    payload["type"] = "refresh"
    payload["exp"] = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    return jwt.encode(
        payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )


def decode_access_token(token: str) -> dict:
    return jwt.decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )