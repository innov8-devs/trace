import uuid
from sqlalchemy import (
    Column,
    String,
    Boolean,
    Enum as SAEnum,
    ForeignKey,
    Float,
    Text
)

from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from ..db.base_class import Base
from ..schemas.listing import Incoterm
from ..schemas.user import UserTier, DocumentStatus


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number = Column(String(15), unique=True, index=True, nullable=False)
    hashed_pin = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    tier = Column(SAEnum(UserTier), default=UserTier.TIER_0, nullable=False)

    # The business this user BELONGS to. This defines the many-to-one relationship.
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=True)
    business = relationship(
        "Business", foreign_keys=[business_id], back_populates="members"
    )

    listings = relationship(
        "Listing", back_populates="seller", cascade="all, delete-orphan"
    )

    # contracts_as_seller = relationship(
    #     "Contract", foreign_keys="[Contract.seller_id]", back_populates="seller"
    # )
    # contracts_as_buyer = relationship(
    #     "Contract", foreign_keys="[Contract.buyer_id]", back_populates="buyer"
    # )


class Business(Base):
    __tablename__ = "businesses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    business_name = Column(String(100), nullable=False)
    cac_number = Column(String(50), unique=True, index=True, nullable=False)
    is_verified = Column(Boolean(), default=False)

    # The designated ADMIN for the business. This is a one-way relationship.
    admin_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    admin = relationship("User", foreign_keys=[admin_id])

    # The list of all MEMBERS belonging to the business.
    # This is the other side of the User.business relationship.
    members = relationship(
        "User", foreign_keys="[User.business_id]", back_populates="business"
    )

    documents = relationship("KYBDocument", back_populates="business")


class KYBDocument(Base):
    __tablename__ = "kyb_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_type = Column(
        String(50), nullable=False
    )  # e.g., "CAC_CERTIFICATE", "TIN_DOCUMENT"
    file_path = Column(String, nullable=False)  # Path to the document in our storage
    status = Column(
        SAEnum(DocumentStatus), default=DocumentStatus.PENDING, nullable=False
    )

    # Relationship to Business
    business_id = Column(
        UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False
    )
    business = relationship("Business", back_populates="documents")

class Listing(Base):
    __tablename__ = "listings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    commodity_name = Column(String(100), index=True, nullable=False)
    quantity_kg = Column(Float, nullable=False)
    price_per_kg_usd = Column(Float, nullable=False)
    location_lga = Column(String(100), index=True)
    location_state = Column(String(50), index=True)
    incoterm = Column(SAEnum(Incoterm), nullable=False)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean(), default=True)

    # Foreign Key to the User who created the listing
    seller_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationship back to the User model
    seller = relationship("User", back_populates="listings")