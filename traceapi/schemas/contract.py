import uuid
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional

from .listing import Listing # We'll need listing details
from .user import User # And user details

class ContractStatus(str, Enum):
    DRAFT = "DRAFT" # Offer made, not yet accepted
    SIGNED = "SIGNED" # Both parties have agreed
    IN_PROGRESS = "IN_PROGRESS" # Execution started (e.g., goods shipped)
    COMPLETED = "COMPLETED"
    DISPUTED = "DISPUTED"
    CANCELLED = "CANCELLED"


# --- Offer Schema ---
# An offer is made by a buyer on a specific listing
class OfferCreate(BaseModel):
    listing_id: uuid.UUID
    # The buyer might offer a slightly different price or quantity
    offered_price_per_kg_usd: float = Field(..., gt=0)


# --- Contract Schemas ---
# The machine-readable component of the Ricardian Contract
class ContractParameters(BaseModel):
    buyer_id: uuid.UUID
    seller_id: uuid.UUID
    listing_id: uuid.UUID
    commodity: str
    quantity_kg: float
    price_per_kg_usd: float
    incoterm: str # Using a simple string for the machine part
    # We will add payment_schedule, shipping_deadlines here later
    # as per the PRD [cite: 56]


# The full Ricardian Contract schema
class Contract(BaseModel):
    id: uuid.UUID
    status: ContractStatus
    # Human-readable legal prose
    legal_prose: str
    # Machine-readable parameters
    parameters: ContractParameters
    # Cryptographic hash of the contract to ensure integrity
    contract_hash: str
    # A link to the on-chain record (placeholder for now) [cite: 56, 62]
    on_chain_id: Optional[str] = None

    buyer: User
    seller: User
    listing: Listing

    class Config:
        from_attributes = True