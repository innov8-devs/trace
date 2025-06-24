from enum import Enum
import uuid
from pydantic import BaseModel, Field
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .user import UserTier

# An enumeration for logistics terms
class Incoterm(str, Enum):
    EXW = "Ex-Works"
    FOB = "Free on Board"
    CIF = "Cost, Insurance, and Freight"


# --- Listing Schemas ---


# Schema for creating a new listing
# This is what the API expects in the request body from a seller
class ListingCreate(BaseModel):
    commodity_name: str = Field(..., max_length=100, examples=["Dried Ginger"])
    quantity_kg: float = Field(..., gt=0, description="Available quantity in kilograms")
    price_per_kg_usd: float = Field(
        ..., gt=0, description="Price per kilogram in USD for stable pricing"
    )
    location_lga: str = Field(
        ...,
        max_length=100,
        description="Local Government Area of the commodity",
        examples=["Kachia"],
    )
    location_state: str = Field(..., max_length=50, examples=["Kaduna"])
    incoterm: Incoterm = Field(default=Incoterm.EXW)
    notes: Optional[str] = None


# Base schema for a listing, containing all shared fields
class ListingBase(ListingCreate):
    id: uuid.UUID
    seller_id: uuid.UUID
    is_active: bool


# UserInDB schema for embedding in listings
class UserInDB(BaseModel):
    id: uuid.UUID
    phone_number: str
    tier: "UserTier"

    class Config:
        from_attributes = True


class Listing(ListingBase):
    seller: UserInDB

    class Config:
        from_attributes = True