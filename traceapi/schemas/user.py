"""
Schemas and data models for the API.
"""

from typing import List
import uuid
from enum import Enum
from pydantic import BaseModel, Field, field_validator
import re
from .listing import Listing


# An enumeration for our user verification tiers
class UserTier(str, Enum):
    """
    Enumeration defining user verification tiers.

    Attributes:
        TIER_0: Phone verified users who can only browse
        TIER_1: BVN/NIN verified users who can transact domestically
        TIER_2: Business KYB verified users who can do international transactions
    """

    TIER_0 = "TIER_0"  # Phone verified, can browse
    TIER_1 = "TIER_1"  # BVN/NIN verified, can transact domestically
    TIER_2 = "TIER_2"  # Business KYB verified, can do international transactions


# An enumeration for the status of a KYC document
class DocumentStatus(str, Enum):
    """
    Enumeration defining document verification statuses.

    Attributes:
        PENDING: Document is awaiting verification
        APPROVED: Document has been verified and approved
        REJECTED: Document verification was rejected
    """

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


# --- User Schemas ---


# Schema for creating a new user (Tier 0)
# This is what the API expects in the request body
class UserCreate(BaseModel):
    """
    Schema for creating a new user account.

    Attributes:
        phone_number (str): User's valid Nigerian phone number, max length 15 chars
        pin (str): User's 4-digit PIN for authentication
    """

    phone_number: str = Field(
        ..., max_length=15, description="User's valid Nigerian phone number"
    )
    pin: str = Field(..., min_length=4, max_length=4, description="User's 4-digit PIN")
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v):
        # Nigerian phone number patterns: +234XXXXXXXXXX, 234XXXXXXXXXX, 0XXXXXXXXXX
        pattern = r'^(\+234|234|0)[789][01]\d{8}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid Nigerian phone number format')
        return v


# Schema for the response when a user is created or retrieved
# This is what the API will send back, notice there is no 'pin' field
class User(BaseModel):
    """
    Schema for user response data without listings.

    Attributes:
        id (UUID): Unique identifier for the user
        phone_number (str): User's phone number
        tier (UserTier): User's verification tier level
        is_active (bool): Whether the user account is active
    """

    id: uuid.UUID
    phone_number: str
    tier: UserTier
    is_active: bool

    class Config:
        """
        User model config
        """

        from_attributes = True  # Formerly orm_mode = True


# Schema for user response data with listings included
class UserWithListings(BaseModel):
    """
    Schema for user response data with listings included.

    Attributes:
        id (UUID): Unique identifier for the user
        phone_number (str): User's phone number
        tier (UserTier): User's verification tier level
        is_active (bool): Whether the user account is active
        listings: List[Listing]: User's items listed on the platform
    """

    id: uuid.UUID
    phone_number: str
    tier: UserTier
    is_active: bool
    listings: List[Listing]

    class Config:
        """
        User model config
        """

        from_attributes = True  # Formerly orm_mode = True


# --- Business Schemas ---


# Schema for creating a new business entity
class BusinessCreate(BaseModel):
    """
    Schema for creating a new business entity.

    Attributes:
        business_name (str): Name of the business, max length 100 chars
        cac_number (str): Corporate Affairs Commission registration number, max length 50 chars
        admin_id (UUID): ID of the user who will be the business admin
    """

    business_name: str = Field(..., max_length=100)
    cac_number: str = Field(..., max_length=50)
    # The user creating the business becomes the default admin
    admin_id: uuid.UUID


# Schema for the business response
class Business(BaseModel):
    """
    Schema for business response data.

    Attributes:
        id (UUID): Unique identifier for the business
        business_name (str): Name of the business
        is_verified (bool): Whether the business has been verified
    """

    id: uuid.UUID
    business_name: str
    is_verified: bool

    class Config:
        """
        Business model config
        """

        from_attributes = True


# --- Token Schema ---
# Schema for the JWT token response on successful login
class Token(BaseModel):
    """
    Schema for JWT authentication token response.

    Attributes:
        access_token (str): The JWT access token
        token_type (str): Type of token (e.g. "bearer")
    """

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Schema for JWT token payload data.

    Attributes:
        phone_number (str, optional): Phone number stored in the token
    """

    phone_number: str | None = None


class LoginRequest(BaseModel):
    """
    Schema for user login data.

    Attributes:
        phone_number (str): User's phone number
        pin (str): User's PIN
    """

    phone_number: str = Field(..., max_length=15)
    pin: str = Field(..., min_length=4, max_length=4)
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v):
        # Nigerian phone number patterns: +234XXXXXXXXXX, 234XXXXXXXXXX, 0XXXXXXXXXX
        pattern = r'^(\+234|234|0)[789][01]\d{8}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid Nigerian phone number format')
        return v

# Rebuild models to resolve forward references
from . import listing
User.model_rebuild()
UserWithListings.model_rebuild()
listing.Listing.model_rebuild()