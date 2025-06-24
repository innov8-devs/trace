from traceapi.utils import dependencies
from traceapi.crud import crud_user
from traceapi.schemas.user import UserCreate, User, Token, LoginRequest
from traceapi.core.security import verify_pin, create_access_token
from traceapi.db import session

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import ValidationError
import uuid

router = APIRouter()


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register_new_user(
    *, db: Session = Depends(session.get_db), create_user_request: UserCreate
):
    """
    Handle new user registration (Tier 0).
    Creates a new user with a phone number and a 4-digit PIN.
    """
    try:
        # Check if a user with this phone number already exists
        user = crud_user.get_user_by_phone(
            db, phone_number=create_user_request.phone_number
        )
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this phone number already exists.",
            )

        # If not, create the new user
        user = crud_user.create_user(db=db, user_in=create_user_request)
        return user
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Nigerian phone number format"
        )


@router.post("/login/token", response_model=Token)
def login_for_access_token(
    login_request: LoginRequest, db: Session = Depends(session.get_db)
):
    """
    Authenticate a user and return a JWT access token.
    """
    try:
        # The form uses 'username', we'll use it for the phone number.
        user = crud_user.get_user_by_phone(db, phone_number=login_request.phone_number)

        # Check if user exists and if the provided PIN is correct
        if not user or not verify_pin(login_request.pin, user.hashed_pin):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect phone number or PIN",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # If credentials are correct, create and return an access token
        access_token = create_access_token(subject=user.phone_number)
        return {"access_token": access_token, "token_type": "bearer"}
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Nigerian phone number format"
        )


@router.get("/profile", response_model=User)
def read_users_me(current_user: User = Depends(dependencies.get_current_user)):
    """
    Fetch the profile of the currently authenticated user.
    """
    # The 'current_user' is injected by our dependency.
    # If the token was invalid or missing, the dependency would have raised an
    # HTTPException, and this code would never even run.
    return current_user


@router.get("/{user_id}", response_model=User)
def get_user_by_id(
    user_id: uuid.UUID, db: Session = Depends(session.get_db)
):
    """
    Fetch a user by their ID.
    """
    user = crud_user.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user
