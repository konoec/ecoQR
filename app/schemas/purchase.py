from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class PurchaseItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    quantity: int = Field(1, ge=1)
    unit_price: Optional[float] = Field(None, ge=0)
    waste_type_id: int
    estimated_weight: float = Field(0.0, ge=0)


class PurchaseCreate(BaseModel):
    branch_id: int
    total_amount: float = Field(..., ge=0)
    currency: str = Field("USD", max_length=3)
    payment_method: Optional[str] = Field(None, max_length=50)
    items: List[PurchaseItemCreate]


class PurchaseItemResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    quantity: int
    unit_price: Optional[float]
    estimated_weight: float
    potential_points: int
    waste_type: Dict[str, Any]  # Waste type information
    
    class Config:
        from_attributes = True


class PurchaseResponse(BaseModel):
    id: int
    purchase_code: str
    total_amount: float
    currency: str
    payment_method: Optional[str]
    estimated_waste_weight: float
    potential_points: int
    environmental_impact_score: float
    qr_code_url: Optional[str]
    qr_expires_at: Optional[datetime]
    is_recycled: bool
    recycled_at: Optional[datetime]
    created_at: datetime
    
    # Related data
    branch: Dict[str, Any]
    items: List[PurchaseItemResponse]
    
    class Config:
        from_attributes = True


class PurchaseList(BaseModel):
    id: int
    purchase_code: str
    total_amount: float
    currency: str
    potential_points: int
    is_recycled: bool
    created_at: datetime
    branch_name: str
    
    class Config:
        from_attributes = True


class QRCodeResponse(BaseModel):
    qr_code_url: str
    qr_code_data: Dict[str, Any]
    expires_at: datetime
    purchase_code: str


class PurchaseStats(BaseModel):
    total_purchases: int
    total_amount_spent: float
    total_potential_points: int
    recycled_purchases: int
    recycling_rate: float
    average_purchase_amount: float
    most_purchased_items: List[Dict[str, Any]]
