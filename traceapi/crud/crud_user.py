from sqlalchemy.orm import Session
from traceapi.db.models import User
from traceapi.schemas.user import UserCreate
from traceapi.core.security import get_pin_hash
import uuid


def get_user_by_phone(db: Session, *, phone_number: str) -> User | None:
    """Fetches a user by their phone number."""
    return db.query(User).filter(User.phone_number == phone_number).first()


def get_user_by_id(db: Session, *, user_id: uuid.UUID) -> User | None:
    """Fetches a user by their ID."""
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, *, user_in: UserCreate) -> User:
    """Creates a new user in the database."""
    # Hash the pin before storing
    hashed_pin = get_pin_hash(user_in.pin)

    # Create the User DB object
    db_user = User(
        phone_number=user_in.phone_number,
        hashed_pin=hashed_pin,
        # Other fields like 'tier' have default values from the model
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
