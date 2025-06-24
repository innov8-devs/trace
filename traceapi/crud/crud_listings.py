import uuid
from sqlalchemy.orm import Session
from traceapi.db.models import Listing
from traceapi.schemas.listing import ListingCreate

def create_listing(db: Session, *, listing_in: ListingCreate, seller_id: uuid.UUID) -> Listing:
    """Creates a new commodity listing in the database."""
    db_listing = Listing(
        **listing_in.model_dump(),
        seller_id=seller_id
    )
    db.add(db_listing)
    db.commit()
    db.refresh(db_listing)
    return db_listing

def get_listings(db: Session, skip: int = 0, limit: int = 100):
    """Fetches all active listings with pagination."""
    return db.query(Listing).filter(Listing.is_active == True).offset(skip).limit(limit).all()

def get_listing_by_id(db: Session, listing_id: uuid.UUID) -> Listing | None:
    """Fetches a single listing by its ID."""
    return db.query(Listing).filter(Listing.id == listing_id).first()