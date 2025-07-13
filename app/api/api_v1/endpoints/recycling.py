from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from loguru import logger
import uuid
from datetime import datetime, timedelta

from app.core.security import get_current_active_user
from app.db.session import get_db, get_mongodb
from app.models.user import User
from app.models.purchase import Purchase
from app.models.recycling import RecyclingEvent, RecyclingItem, RecyclingStatus, ValidationStatus
from app.models.branch import Branch
from app.schemas.recycling import (
    ScanQRRequest,
    QRScanResponse,
    ValidateRecyclingRequest,
    ValidationResponse,
    RecyclingEventResponse,
    RecyclingEventList
)
from app.services.qr_service import validate_qr_code
from app.services.ai_validation import validate_recycling_classification
from app.core.exceptions import NotFoundError, ValidationError, BusinessLogicError

router = APIRouter()


@router.post("/scan-qr", response_model=QRScanResponse)
async def scan_qr_code(
    scan_request: ScanQRRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Scan QR code to start recycling process"""
    
    try:
        # Validate and decode QR code
        qr_data = await validate_qr_code(scan_request.qr_code_data)
        
        # Verify purchase exists and belongs to user
        purchase = db.query(Purchase).filter(
            Purchase.id == qr_data['purchase_id'],
            Purchase.user_id == current_user.id
        ).first()
        
        if not purchase:
            raise NotFoundError("Purchase not found or access denied")
        
        # Check if QR code has expired
        if purchase.qr_expires_at and purchase.qr_expires_at < datetime.utcnow():
            raise ValidationError("QR code has expired")
        
        # Check if purchase has already been recycled
        if purchase.is_recycled:
            raise BusinessLogicError("This purchase has already been recycled")
        
        # Create recycling event
        event_code = f"REC-{uuid.uuid4().hex[:8].upper()}"
        
        recycling_event = RecyclingEvent(
            event_code=event_code,
            user_id=current_user.id,
            purchase_id=purchase.id,
            branch_id=purchase.branch_id,
            status=RecyclingStatus.PENDING,
            validation_status=ValidationStatus.PENDING,
            points_potential=purchase.potential_points,
            qr_scanned_at=datetime.utcnow()
        )
        
        db.add(recycling_event)
        db.flush()
        
        # Create recycling items based on purchase items
        items_to_recycle = []
        for purchase_item in purchase.items:
            recycling_item = RecyclingItem(
                recycling_event_id=recycling_event.id,
                waste_type_id=purchase_item.waste_type_id,
                name=purchase_item.name,
                quantity=purchase_item.quantity,
                weight_recycled=0.0,  # Will be updated after validation
                points_potential=purchase_item.potential_points
            )
            db.add(recycling_item)
            
            items_to_recycle.append({
                "name": purchase_item.name,
                "waste_type": purchase_item.waste_type.name,
                "category": purchase_item.waste_type.category,
                "bin_color": purchase_item.waste_type.bin_color,
                "instructions": purchase_item.waste_type.recycling_instructions,
                "quantity": purchase_item.quantity,
                "potential_points": purchase_item.potential_points
            })
        
        db.commit()
        
        # Log to MongoDB
        mongo_db = get_mongodb()
        await mongo_db.recycling_events.insert_one({
            "recycling_event_id": recycling_event.id,
            "event_code": event_code,
            "user_id": current_user.id,
            "purchase_id": purchase.id,
            "branch_id": purchase.branch_id,
            "action": "qr_scanned",
            "timestamp": datetime.utcnow(),
            "location": scan_request.location,
            "items_count": len(items_to_recycle)
        })
        
        logger.info(f"QR code scanned successfully: {event_code} for user {current_user.email}")
        
        return QRScanResponse(
            success=True,
            message="QR code scanned successfully. Please proceed to validate recycling.",
            recycling_event_id=recycling_event.id,
            purchase_info={
                "purchase_code": purchase.purchase_code,
                "total_amount": purchase.total_amount,
                "branch_name": purchase.branch.name,
                "potential_points": purchase.potential_points
            },
            items_to_recycle=items_to_recycle,
            instructions="Please place each item in the correct recycling bin and take a photo for validation."
        )
        
    except Exception as e:
        logger.error(f"QR scan failed: {str(e)}")
        raise


@router.post("/validate", response_model=ValidationResponse)
async def validate_recycling(
    validation_request: ValidateRecyclingRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Validate recycling classification using AI"""
    
    # Get recycling event
    recycling_event = db.query(RecyclingEvent).filter(
        RecyclingEvent.id == validation_request.recycling_event_id,
        RecyclingEvent.user_id == current_user.id
    ).first()
    
    if not recycling_event:
        raise NotFoundError("Recycling event not found")
    
    if recycling_event.status != RecyclingStatus.PENDING:
        raise BusinessLogicError("Recycling event is not in pending status")
    
    try:
        # Update status to in progress
        recycling_event.status = RecyclingStatus.IN_PROGRESS
        recycling_event.validation_started_at = datetime.utcnow()
        db.commit()
        
        # Call AI validation service
        ai_result = await validate_recycling_classification(
            image_data=validation_request.image_data,
            expected_items=[
                {
                    "waste_type_id": item.waste_type_id,
                    "name": item.name,
                    "category": item.waste_type.category
                }
                for item in recycling_event.items
            ]
        )
        
        # Process validation results
        total_points = 0
        correct_classifications = 0
        total_items = len(validation_request.items_validation)
        feedback = []
        
        for i, item_validation in enumerate(validation_request.items_validation):
            recycling_item = recycling_event.items[i]
            
            # Update recycling item with validation results
            recycling_item.is_correctly_classified = item_validation.is_correctly_classified
            recycling_item.predicted_bin = item_validation.predicted_bin
            recycling_item.confidence_score = item_validation.confidence_score
            
            if item_validation.is_correctly_classified:
                correct_classifications += 1
                recycling_item.points_awarded = recycling_item.points_potential
                recycling_item.weight_recycled = ai_result.get("estimated_weights", [0.1])[i]
                total_points += recycling_item.points_awarded
                
                feedback.append({
                    "item": recycling_item.name,
                    "status": "correct",
                    "message": f"Correctly classified! Earned {recycling_item.points_awarded} points.",
                    "bin_color": recycling_item.waste_type.bin_color
                })
            else:
                recycling_item.points_awarded = 0
                recycling_item.rejected_reason = "Incorrect classification"
                
                feedback.append({
                    "item": recycling_item.name,
                    "status": "incorrect",
                    "message": f"Incorrect classification. Should go in {recycling_item.waste_type.bin_color} bin.",
                    "correct_bin": recycling_item.waste_type.bin_color
                })
        
        # Calculate accuracy and update event
        accuracy_score = (correct_classifications / total_items) * 100
        recycling_event.accuracy_score = accuracy_score
        recycling_event.points_earned = total_points
        recycling_event.validation_status = ValidationStatus.VALIDATED
        recycling_event.status = RecyclingStatus.COMPLETED
        recycling_event.validation_completed_at = datetime.utcnow()
        recycling_event.ai_validation_id = ai_result.get("validation_id")
        recycling_event.ai_confidence_score = ai_result.get("overall_confidence", 0.0)
        
        # Calculate environmental impact
        recycling_event.calculate_environmental_impact()
        
        # Update user points
        current_user.add_points(total_points)
        current_user.total_recycled_items += correct_classifications
        current_user.carbon_footprint_reduced += recycling_event.carbon_footprint_reduced
        
        # Mark purchase as recycled
        purchase = recycling_event.purchase
        purchase.is_recycled = True
        purchase.recycled_at = datetime.utcnow()
        
        # Update branch statistics
        branch = recycling_event.branch
        branch.update_recycling_stats(correct_classifications, recycling_event.carbon_footprint_reduced)
        
        db.commit()
        
        # Log to MongoDB
        mongo_db = get_mongodb()
        await mongo_db.ai_validations.insert_one({
            "validation_id": ai_result.get("validation_id"),
            "recycling_event_id": recycling_event.id,
            "user_id": current_user.id,
            "accuracy_score": accuracy_score,
            "points_earned": total_points,
            "ai_confidence": ai_result.get("overall_confidence", 0.0),
            "items_validated": total_items,
            "correct_classifications": correct_classifications,
            "timestamp": datetime.utcnow(),
            "processing_time": ai_result.get("processing_time", 0.0)
        })
        
        logger.info(
            f"Recycling validated: {recycling_event.event_code} - "
            f"Accuracy: {accuracy_score:.1f}% - Points: {total_points}"
        )
        
        # Determine next steps message
        if accuracy_score >= 80:
            next_steps = "Excellent recycling! Keep up the great work."
        elif accuracy_score >= 60:
            next_steps = "Good effort! Review the feedback to improve your recycling accuracy."
        else:
            next_steps = "Please review the recycling guidelines and try again next time."
        
        return ValidationResponse(
            success=True,
            message=f"Recycling validation completed with {accuracy_score:.1f}% accuracy.",
            points_earned=total_points,
            accuracy_score=accuracy_score,
            feedback=feedback,
            next_steps=next_steps
        )
        
    except Exception as e:
        # Rollback status on error
        recycling_event.status = RecyclingStatus.FAILED
        recycling_event.validation_status = ValidationStatus.REJECTED
        db.commit()
        
        logger.error(f"Recycling validation failed: {str(e)}")
        raise


@router.get("/history", response_model=List[RecyclingEventList])
async def get_recycling_history(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    limit: int = 20,
    offset: int = 0
):
    """Get user's recycling history"""
    
    events = db.query(RecyclingEvent).filter(
        RecyclingEvent.user_id == current_user.id
    ).order_by(RecyclingEvent.created_at.desc()).offset(offset).limit(limit).all()
    
    result = []
    for event in events:
        result.append(RecyclingEventList(
            id=event.id,
            event_code=event.event_code,
            status=event.status,
            points_earned=event.points_earned,
            accuracy_score=event.accuracy_score,
            created_at=event.created_at,
            purchase_code=event.purchase.purchase_code,
            branch_name=event.branch.name
        ))
    
    return result


@router.get("/{event_id}", response_model=RecyclingEventResponse)
async def get_recycling_event_details(
    event_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a recycling event"""
    
    event = db.query(RecyclingEvent).filter(
        RecyclingEvent.id == event_id,
        RecyclingEvent.user_id == current_user.id
    ).first()
    
    if not event:
        raise NotFoundError("Recycling event not found")
    
    # Build response with related data
    response_data = {
        **event.__dict__,
        "purchase": {
            "id": event.purchase.id,
            "purchase_code": event.purchase.purchase_code,
            "total_amount": event.purchase.total_amount
        },
        "items": []
    }
    
    for item in event.items:
        response_data["items"].append({
            **item.__dict__,
            "waste_type": {
                "id": item.waste_type.id,
                "name": item.waste_type.name,
                "category": item.waste_type.category,
                "bin_color": item.waste_type.bin_color
            }
        })
    
    return RecyclingEventResponse(**response_data)
