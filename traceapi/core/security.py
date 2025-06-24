from datetime import datetime, timedelta, timezone
from typing import Any

from traceapi.core.config import settings

from jose import jwt
from passlib.context import CryptContext

# We use passlib to handle password hashing. bcrypt is a strong hashing algorithm.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_pin(plain_pin: str, hashed_pin: str) -> bool:
    """Verifies a plain text PIN against a hashed PIN."""
    return pwd_context.verify(plain_pin, hashed_pin)


def get_pin_hash(pin: str) -> str:
    """Hashes a plain text PIN."""
    return pwd_context.hash(pin)


def create_access_token(subject: Any, expires_delta: timedelta | None = None) -> str:
    """
    Creates a new JWT access token.
    The 'subject' of the token will be the user's phone number.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt
