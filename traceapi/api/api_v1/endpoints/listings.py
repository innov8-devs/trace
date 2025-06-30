import uuid
from typing import List

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session

from traceapi.crud.crud_contract import create_contract_from_listing
from traceapi.crud.crud_listings import create_listing, get_listings, get_listing_by_id
from traceapi.db import session, models
from traceapi.schemas.contract import Contract
from traceapi.schemas.listing import Listing, ListingCreate
from traceapi.schemas.user import User
from traceapi.utils import dependencies

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

@router.post("/{listing_id}/make-offer", response_model=Contract)
def make_offer_on_listing(
        *,
        db: Session = Depends(session.get_db),
        listing_id: uuid.UUID,
        # In a real scenario, the offer_in would contain price, etc.
        # offer_in: schemas.OfferCreate,
        current_user: models.User = Depends(dependencies.get_current_user)
):
    """
    A buyer makes an offer on a listing, creating a DRAFT contract.
    This action corresponds to the "Create Contract" button in the PRD[cite: 56].
    """
    listing = get_listing_by_id(db, listing_id=listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if not listing.is_active:
        raise HTTPException(status_code=400, detail="Listing is not active")
    if listing.seller_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot make an offer on your own listing")

    # For now, making an offer directly creates the contract in DRAFT state
    contract = create_contract_from_listing(db=db, listing=listing, buyer=current_user)

    return contract