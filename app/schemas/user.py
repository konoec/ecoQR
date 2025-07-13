from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    preferred_language: str = Field("es", max_length=5)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    preferred_language: Optional[str] = Field(None, max_length=5)
    profile_image_url: Optional[str] = Field(None, max_length=500)


class UserInDB(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    is_verified: bool
    total_points: int
    total_recycled_items: int
    carbon_footprint_reduced: float
    profile_image_url: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True


class User(UserInDB):
    """User response schema"""
    pass


class UserProfile(BaseModel):
    """Detailed user profile with statistics"""
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    full_name: str
    phone: Optional[str]
    profile_image_url: Optional[str]
    preferred_language: str
    
    # Statistics
    total_points: int
    total_recycled_items: int
    carbon_footprint_reduced: float
    
    # Account info
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    # Recent activity counts
    recent_purchases: Optional[int] = None
    recent_recycling_events: Optional[int] = None
    recent_rewards_redeemed: Optional[int] = None
    
    class Config:
        from_attributes = True


class UserStats(BaseModel):
    """User environmental statistics"""
    total_points: int
    total_recycled_items: int
    carbon_footprint_reduced: float
    recycling_accuracy_rate: float
    favorite_waste_categories: List[str]
    monthly_recycling_count: int
    ranking_position: Optional[int] = None
    
    class Config:
        from_attributes = True


class UserList(BaseModel):
    """User list item for admin purposes"""
    id: int
    email: EmailStr
    full_name: str
    total_points: int
    total_recycled_items: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class PasswordChange(BaseModel):
    """Schema for password change"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v
