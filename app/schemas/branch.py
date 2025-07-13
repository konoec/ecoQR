from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class BranchBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    address: str = Field(..., min_length=1)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    country: str = Field(..., min_length=1, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    manager_name: Optional[str] = Field(None, max_length=200)
    opening_hours: Optional[str] = None


class BranchCreate(BranchBase):
    pass


class BranchUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    address: Optional[str] = Field(None, min_length=1)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    state: Optional[str] = Field(None, min_length=1, max_length=100)
    country: Optional[str] = Field(None, min_length=1, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    manager_name: Optional[str] = Field(None, max_length=200)
    opening_hours: Optional[str] = None
    is_active: Optional[bool] = None


class Branch(BranchBase):
    id: int
    is_active: bool
    total_recycled_items: int
    total_carbon_reduced: float
    recycling_accuracy_rate: float
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class BranchList(BaseModel):
    id: int
    name: str
    city: str
    state: str
    country: str
    is_active: bool
    total_recycled_items: int
    
    class Config:
        from_attributes = True


class BranchStats(BaseModel):
    id: int
    name: str
    total_recycled_items: int
    total_carbon_reduced: float
    recycling_accuracy_rate: float
    monthly_recycling_count: int
    most_recycled_categories: List[Dict[str, Any]]
    top_users: List[Dict[str, Any]]
    
    class Config:
        from_attributes = True
