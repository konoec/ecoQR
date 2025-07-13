from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class RecyclingStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ValidationStatus(str, Enum):
    PENDING = "pending"
    VALIDATED = "validated"
    REJECTED = "rejected"
    MANUAL_REVIEW = "manual_review"


class RecyclingItemValidation(BaseModel):
    waste_type_id: int
    is_correctly_classified: bool
    predicted_bin: str
    confidence_score: float = Field(..., ge=0, le=100)


class ScanQRRequest(BaseModel):
    qr_code_data: str
    location: Optional[Dict[str, float]] = None  # {"latitude": x, "longitude": y}


class ValidateRecyclingRequest(BaseModel):
    recycling_event_id: int
    image_data: str  # Base64 encoded image
    items_validation: List[RecyclingItemValidation]


class RecyclingEventResponse(BaseModel):
    id: int
    event_code: str
    status: RecyclingStatus
    validation_status: ValidationStatus
    points_earned: int
    points_potential: int
    accuracy_score: float
    total_weight_recycled: float
    carbon_footprint_reduced: float
    qr_scanned_at: Optional[datetime]
    validation_completed_at: Optional[datetime]
    created_at: datetime
    
    # Related data
    purchase: Dict[str, Any]
    items: List[Dict[str, Any]]
    
    class Config:
        from_attributes = True


class RecyclingEventList(BaseModel):
    id: int
    event_code: str
    status: RecyclingStatus
    points_earned: int
    accuracy_score: float
    created_at: datetime
    purchase_code: str
    branch_name: str
    
    class Config:
        from_attributes = True


class RecyclingStats(BaseModel):
    total_events: int
    completed_events: int
    total_points_earned: int
    average_accuracy: float
    total_weight_recycled: float
    carbon_footprint_reduced: float
    favorite_categories: List[str]
    monthly_events: int


class QRScanResponse(BaseModel):
    """Response when QR code is successfully scanned"""
    success: bool
    message: str
    recycling_event_id: int
    purchase_info: Dict[str, Any]
    items_to_recycle: List[Dict[str, Any]]
    instructions: str


class ValidationResponse(BaseModel):
    """Response after AI validation"""
    success: bool
    message: str
    points_earned: int
    accuracy_score: float
    feedback: List[Dict[str, Any]]
    next_steps: str
