from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from traceapi.crud import crud_user
from traceapi.db import models
from traceapi.schemas import user as UserSchema
from traceapi.core.config import settings
from traceapi.db.session import get_db

# HTTP Bearer scheme for JWT tokens
bearer = HTTPBearer()


def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
) -> models.User:
    """
    Dependency to get the current authenticated user.
    Decodes the JWT token from the request and retrieves the user from the database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Extract the token string from HTTPAuthorizationCredentials
        token = credentials.credentials

        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        phone_number: str = payload.get("sub")
        if phone_number is None:
            raise credentials_exception
        token_data = UserSchema.TokenData(phone_number=phone_number)
    except JWTError as exc:
        raise credentials_exception from exc

    user = crud_user.get_user_by_phone(db, phone_number=token_data.phone_number)
    if user is None:
        raise credentials_exception

    return user


def get_token(credentials: HTTPAuthorizationCredentials = Depends(bearer)) -> str:
    """
    Dependency to extract just the token string from the Bearer token.
    """
    return credentials.credentials
