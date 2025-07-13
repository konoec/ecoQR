from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class RewardType(str, Enum):
    DISCOUNT = "discount"
    FREE_ITEM = "free_item"
    VOUCHER = "voucher"
    EXPERIENCE = "experience"
    MERCHANDISE = "merchandise"


class RewardStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    OUT_OF_STOCK = "out_of_stock"


class UserRewardStatus(str, Enum):
    ACTIVE = "active"
    USED = "used"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class RewardBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    type: RewardType
    points_required: int = Field(..., ge=0)
    monetary_value: float = Field(0.0, ge=0)
    currency: str = Field("USD", max_length=3)
    discount_percentage: Optional[float] = Field(None, ge=0, le=100)
    discount_amount: Optional[float] = Field(None, ge=0)
    total_quantity: Optional[int] = Field(None, ge=0)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    usage_limit_per_user: int = Field(1, ge=1)
    image_url: Optional[str] = Field(None, max_length=500)
    terms_and_conditions: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    minimum_purchase_amount: Optional[float] = Field(None, ge=0)


class RewardCreate(RewardBase):
    pass


class RewardUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    points_required: Optional[int] = Field(None, ge=0)
    monetary_value: Optional[float] = Field(None, ge=0)
    discount_percentage: Optional[float] = Field(None, ge=0, le=100)
    discount_amount: Optional[float] = Field(None, ge=0)
    total_quantity: Optional[int] = Field(None, ge=0)
    remaining_quantity: Optional[int] = Field(None, ge=0)
    status: Optional[RewardStatus] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    image_url: Optional[str] = Field(None, max_length=500)
    terms_and_conditions: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)


class Reward(RewardBase):
    id: int
    remaining_quantity: Optional[int]
    status: RewardStatus
    total_redeemed: int
    popularity_score: float
    is_available: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class RewardList(BaseModel):
    id: int
    name: str
    type: RewardType
    points_required: int
    monetary_value: float
    image_url: Optional[str]
    is_available: bool
    remaining_quantity: Optional[int]
    category: Optional[str]
    
    class Config:
        from_attributes = True


class RedeemRewardRequest(BaseModel):
    reward_id: int
    notes: Optional[str] = None


class UserRewardResponse(BaseModel):
    id: int
    redemption_code: str
    status: UserRewardStatus
    points_spent: int
    expires_at: Optional[datetime]
    qr_code_url: Optional[str]
    created_at: datetime
    used_at: Optional[datetime]
    
    # Related data
    reward: Dict[str, Any]
    
    class Config:
        from_attributes = True


class UserRewardList(BaseModel):
    id: int
    redemption_code: str
    status: UserRewardStatus
    points_spent: int
    expires_at: Optional[datetime]
    created_at: datetime
    reward_name: str
    reward_type: RewardType
    is_valid: bool
    
    class Config:
        from_attributes = True


class RewardStats(BaseModel):
    total_rewards_available: int
    total_redeemed: int
    points_spent: int
    active_user_rewards: int
    expired_user_rewards: int
    most_popular_rewards: List[Dict[str, Any]]
