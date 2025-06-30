import uuid
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from traceapi.crud import crud_contract
from traceapi.crud.crud_contract import get_contract_by_id, accept_contract, create_contract_from_listing
from traceapi.crud.crud_listings import get_listing_by_id
from traceapi.db import session
from traceapi.db.models import User
from traceapi.schemas.contract import Contract, ContractStatus, OfferCreate
from traceapi.utils import dependencies

router = APIRouter()

@router.post("/offers", response_model=Contract, status_code=HTTPStatus.CREATED)
def make_offer_on_listing(
        *,
        db: Session = Depends(session.get_db),
        offer_in: OfferCreate,
        current_user: User = Depends(dependencies.get_current_user)
):
    """
    A buyer makes an offer on a listing, creating a DRAFT contract.
    """
    listing = get_listing_by_id(db, listing_id=offer_in.listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if not listing.is_active:
        raise HTTPException(status_code=400, detail="Listing is not active")
    if listing.seller_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot make an offer on your own listing")

    contract = create_contract_from_listing(db=db, listing=listing, buyer=current_user)

    return contract

@router.get("/{contract_id}", response_model=Contract)
def read_contract(
        *,
        db: Session = Depends(session.get_db),
        contract_id: uuid.UUID,
        current_user: User = Depends(dependencies.get_current_user)
):
    """
    Retrieve a specific contract.
    A user can only view a contract if they are the buyer or the seller.
    """
    contract = crud_contract.get_contract_by_id(db, contract_id=contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    if contract.buyer_id != current_user.id and contract.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this contract")

    return contract


@router.post("/{contract_id}/accept", response_model=Contract)
def accept_trade_contract(
        *,
        db: Session = Depends(session.get_db),
        contract_id: uuid.UUID,
        current_user: User = Depends(dependencies.get_current_user)
):
    """
    Seller accepts a DRAFT contract, changing its status to SIGNED.
    This is the digital signature action. Once signed, the contract is locked.
    """
    contract = get_contract_by_id(db, contract_id=contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    # --- Authorization Check ---
    # Ensure the person accepting is the seller and not the buyer
    if contract.seller_id != current_user.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Only the seller can accept the contract",
        )

    # --- State Machine Check ---
    # Ensure the contract is in DRAFT status before accepting
    if contract.status != ContractStatus.DRAFT:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Contract cannot be accepted. Current status: {contract.status}",
        )

    # If all checks pass, update the contract
    accepted_contract = accept_contract(db=db, contract=contract)

    # As per the PRD, once signed, the contract is locked and a record is stored.
    # Our hash already ensures integrity. The next step would be storing the hash on-chain.
    # [cite: 56]
    return accepted_contract