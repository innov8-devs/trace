import uuid
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from typing import Optional

class TransactionType(str, Enum):
    DEPOSIT = "DEPOSIT" # Funding a wallet (on-ramp)
    WITHDRAWAL = "WITHDRAWAL" # Cashing out (off-ramp)
    ESCROW = "ESCROW" # Moving funds into escrow for a trade
    RELEASE = "RELEASE" # Releasing funds from escrow to seller
    REFUND = "REFUND" # Refunding buyer from escrow

class TransactionStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

# --- Wallet Schema ---
class Wallet(BaseModel):
    id: uuid.UUID
    owner_id: uuid.UUID
    # We will track balances in cents to avoid floating point issues
    balance_usd_cents: int = Field(..., description="Balance in USDC, represented in cents")

    class Config:
        from_attributes = True


# --- Transaction Schema ---
class Transaction(BaseModel):
    id: uuid.UUID
    wallet_id: uuid.UUID
    contract_id: Optional[uuid.UUID] = None
    transaction_type: TransactionType
    status: TransactionStatus
    amount_usd_cents: int
    created_at: datetime

    class Config:
        from_attributes = True