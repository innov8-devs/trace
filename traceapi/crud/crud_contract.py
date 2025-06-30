import hashlib
import uuid
from datetime import datetime
import json
from sqlalchemy.orm import Session
from traceapi.db.models import Contract, Listing, User
from traceapi.schemas.contract import ContractParameters, ContractStatus


def generate_legal_prose(params: ContractParameters) -> str:
    """
    Generates human-readable legal text from contract parameters.
    This would be a template validated by Nigerian legal experts[cite: 63].
    """
    prose = f"""
    --- LEGAL TRADE AGREEMENT ---
    This contract is made on {datetime.now().strftime('%Y-%m-%d')}.
    
    PARTIES:
    - Seller ID: {params.seller_id}
    - Buyer ID: {params.buyer_id}
    
    TERMS:
    - Commodity: {params.commodity}
    - Quantity: {params.quantity_kg} kg
    - Price: USD ${params.price_per_kg_usd}/kg
    - Incoterm: {params.incoterm}
    
    This agreement is governed by the laws of Nigeria. Both parties agree to the 
    terms and conditions as laid out on the Farmily TRACE platform. Digital acceptance 
    of this contract constitutes a legally binding signature.
    """
    return prose.strip()

def create_contract_from_listing(db: Session, *, listing: Listing, buyer: User) -> Contract:
    """
    Creates a new contract in DRAFT status based on an offer for a listing.
    """
    # 1. Define the machine-readable parameters [cite: 60]
    params = ContractParameters(
        buyer_id=str(buyer.id),
        seller_id=str(listing.seller_id),
        listing_id=str(listing.id),
        commodity=listing.commodity_name,
        quantity_kg=listing.quantity_kg,
        price_per_kg_usd=listing.price_per_kg_usd,
        incoterm=listing.incoterm.value
    )

    # 2. Generate the human-readable legal prose [cite: 59]
    legal_prose = generate_legal_prose(params)

    # 3. Create the cryptographic hash of the contract to ensure it's tamper-proof [cite: 61]
    contract_data_string = legal_prose + json.dumps(params.model_dump(mode='json'), sort_keys=True)
    contract_hash = hashlib.sha256(contract_data_string.encode()).hexdigest()

    # 4. Create the database object
    db_contract = Contract(
        listing_id=listing.id,
        seller_id=listing.seller_id,
        buyer_id=buyer.id,
        legal_prose=legal_prose,
        parameters=params.model_dump(mode='json'),
        contract_hash=contract_hash
    )

    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)
    return db_contract

def get_contract_by_id(db: Session, *, contract_id: uuid.UUID) -> Contract | None:
    """Fetches a single contract by its ID."""
    return db.query(Contract).filter(Contract.id == contract_id).first()

def accept_contract(db: Session, *, contract: Contract) -> Contract:
    """
    Updates a contract's status to SIGNED.
    """
    contract.status = ContractStatus.SIGNED
    # Here is where we would later add a hook to trigger the escrow funding process
    # for the Payments & Settlement module.
    db.add(contract)
    db.commit()
    db.refresh(contract)
    return contract