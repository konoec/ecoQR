from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from loguru import logger
import uuid
from datetime import datetime, timedelta

from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.models.purchase import Purchase, PurchaseItem
from app.models.branch import Branch
from app.models.waste_type import WasteType
from app.schemas.purchase import (
    PurchaseCreate,
    PurchaseResponse,
    QRCodeResponse,
    PurchaseList
)
from app.services.qr_service import generate_qr_code
from app.core.exceptions import NotFoundError, ValidationError

router = APIRouter()


@router.post("/", response_model=PurchaseResponse)
async def create_purchase(
    purchase_data: PurchaseCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new purchase and generate QR code"""
    
    # Validate branch exists
    branch = db.query(Branch).filter(Branch.id == purchase_data.branch_id).first()
    if not branch:
        raise NotFoundError("Branch not found")
    
    # Validate waste types for items
    waste_type_ids = [item.waste_type_id for item in purchase_data.items]
    waste_types = db.query(WasteType).filter(WasteType.id.in_(waste_type_ids)).all()
    waste_type_dict = {wt.id: wt for wt in waste_types}
    
    if len(waste_types) != len(waste_type_ids):
        raise ValidationError("One or more waste types not found")
    
    # Generate unique purchase code
    purchase_code = f"ECO-{uuid.uuid4().hex[:8].upper()}"
    
    # Create purchase
    purchase = Purchase(
        purchase_code=purchase_code,
        user_id=current_user.id,
        branch_id=purchase_data.branch_id,
        total_amount=purchase_data.total_amount,
        currency=purchase_data.currency,
        payment_method=purchase_data.payment_method,
        qr_expires_at=datetime.utcnow() + timedelta(hours=24)  # QR expires in 24 hours
    )
    
    db.add(purchase)
    db.flush()  # Get the purchase ID
    
    # Create purchase items
    total_potential_points = 0
    total_estimated_weight = 0.0
    
    for item_data in purchase_data.items:
        waste_type = waste_type_dict[item_data.waste_type_id]
        
        # Calculate potential points
        potential_points = waste_type.recycling_points * item_data.quantity
        total_potential_points += potential_points
        total_estimated_weight += item_data.estimated_weight
        
        purchase_item = PurchaseItem(
            purchase_id=purchase.id,
            waste_type_id=item_data.waste_type_id,
            name=item_data.name,
            description=item_data.description,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            estimated_weight=item_data.estimated_weight,
            potential_points=potential_points
        )
        
        db.add(purchase_item)
    
    # Update purchase totals
    purchase.potential_points = total_potential_points
    purchase.estimated_waste_weight = total_estimated_weight
    purchase.calculate_environmental_impact()
    
    # Generate QR code
    qr_data = {
        "purchase_id": purchase.id,
        "purchase_code": purchase_code,
        "user_id": current_user.id,
        "branch_id": purchase_data.branch_id,
        "items": [
            {
                "name": item.name,
                "waste_type_id": item.waste_type_id,
                "waste_type_name": waste_type_dict[item.waste_type_id].name,
                "waste_type_category": waste_type_dict[item.waste_type_id].category,
                "bin_color": waste_type_dict[item.waste_type_id].bin_color,
                "quantity": item.quantity,
                "points": item.potential_points
            }
            for item in purchase_data.items
        ]
    }
    
    qr_code_url = await generate_qr_code(qr_data)
    purchase.set_qr_data(qr_data)
    purchase.qr_code_url = qr_code_url
    
    db.commit()
    db.refresh(purchase)
    
    logger.info(f"Purchase created: {purchase_code} for user {current_user.email}")
    
    # Build response
    response_data = {
        **purchase.__dict__,
        "branch": {"id": branch.id, "name": branch.name, "address": branch.address},
        "items": []
    }
    
    for item in purchase.items:
        waste_type = waste_type_dict[item.waste_type_id]
        response_data["items"].append({
            **item.__dict__,
            "waste_type": {
                "id": waste_type.id,
                "name": waste_type.name,
                "category": waste_type.category,
                "bin_color": waste_type.bin_color
            }
        })
    
    return PurchaseResponse(**response_data)


@router.get("/{purchase_id}/qr", response_model=QRCodeResponse)
async def get_purchase_qr(
    purchase_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get QR code for a purchase"""
    
    purchase = db.query(Purchase).filter(
        Purchase.id == purchase_id,
        Purchase.user_id == current_user.id
    ).first()
    
    if not purchase:
        raise NotFoundError("Purchase not found")
    
    if purchase.qr_expires_at and purchase.qr_expires_at < datetime.utcnow():
        raise ValidationError("QR code has expired")
    
    if purchase.is_recycled:
        raise ValidationError("Purchase has already been recycled")
    
    return QRCodeResponse(
        qr_code_url=purchase.qr_code_url,
        qr_code_data=purchase.qr_data_dict,
        expires_at=purchase.qr_expires_at,
        purchase_code=purchase.purchase_code
    )


@router.get("/", response_model=List[PurchaseList])
async def get_user_purchases(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    limit: int = 20,
    offset: int = 0
):
    """Get user's purchase history"""
    
    purchases = db.query(Purchase).filter(
        Purchase.user_id == current_user.id
    ).order_by(Purchase.created_at.desc()).offset(offset).limit(limit).all()
    
    result = []
    for purchase in purchases:
        result.append(PurchaseList(
            id=purchase.id,
            purchase_code=purchase.purchase_code,
            total_amount=purchase.total_amount,
            currency=purchase.currency,
            potential_points=purchase.potential_points,
            is_recycled=purchase.is_recycled,
            created_at=purchase.created_at,
            branch_name=purchase.branch.name
        ))
    
    return result


@router.get("/{purchase_id}", response_model=PurchaseResponse)
async def get_purchase_details(
    purchase_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific purchase"""
    
    purchase = db.query(Purchase).filter(
        Purchase.id == purchase_id,
        Purchase.user_id == current_user.id
    ).first()
    
    if not purchase:
        raise NotFoundError("Purchase not found")
    
    # Build response with related data
    response_data = {
        **purchase.__dict__,
        "branch": {
            "id": purchase.branch.id,
            "name": purchase.branch.name,
            "address": purchase.branch.address
        },
        "items": []
    }
    
    for item in purchase.items:
        response_data["items"].append({
            **item.__dict__,
            "waste_type": {
                "id": item.waste_type.id,
                "name": item.waste_type.name,
                "category": item.waste_type.category,
                "bin_color": item.waste_type.bin_color
            }
        })
    
    return PurchaseResponse(**response_data)
