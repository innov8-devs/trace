from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from traceapi.utils import dependencies
from traceapi.crud.crud_listings import create_listing, get_listings
from traceapi.db import session
from traceapi.schemas.listing import Listing, ListingCreate
from traceapi.schemas.user import User

router = APIRouter()

@router.post("/", response_model=Listing, status_code=status.HTTP_201_CREATED)
def create_new_listing(
        *,
        db: Session = Depends(session.get_db),
        listing_in: ListingCreate,
        current_user: User = Depends(dependencies.get_current_user)
):
    """
    Create a new commodity listing. This is a protected endpoint.
    """
    listing = create_listing(db=db, listing_in=listing_in, seller_id=current_user.id)
    return listing

@router.get("/", response_model=List[Listing])
def read_active_listings(
        db: Session = Depends(session.get_db),
        skip: int = 0,
        limit: int = 100
):
    """
    Retrieve all active listings. This is a public endpoint.
    """
    listings = get_listings(db, skip=skip, limit=limit)
    return listings