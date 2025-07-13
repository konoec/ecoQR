from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import enum


class RewardType(str, enum.Enum):
    DISCOUNT = "discount"
    FREE_ITEM = "free_item"
    VOUCHER = "voucher"
    EXPERIENCE = "experience"
    MERCHANDISE = "merchandise"


class RewardStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    OUT_OF_STOCK = "out_of_stock"


class UserRewardStatus(str, enum.Enum):
    ACTIVE = "active"
    USED = "used"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class Reward(Base):
    __tablename__ = "rewards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(Enum(RewardType), nullable=False)
    
    # Cost and value
    points_required = Column(Integer, nullable=False)
    monetary_value = Column(Float, default=0.0)
    currency = Column(String(3), default="USD")
    
    # Discount details (for discount type rewards)
    discount_percentage = Column(Float, nullable=True)
    discount_amount = Column(Float, nullable=True)
    
    # Availability
    total_quantity = Column(Integer, nullable=True)  # null = unlimited
    remaining_quantity = Column(Integer, nullable=True)
    status = Column(Enum(RewardStatus), default=RewardStatus.ACTIVE)
    
    # Validity
    valid_from = Column(DateTime(timezone=True), nullable=True)
    valid_until = Column(DateTime(timezone=True), nullable=True)
    usage_limit_per_user = Column(Integer, default=1)
    
    # Visual and content
    image_url = Column(String(500), nullable=True)
    icon_url = Column(String(500), nullable=True)
    terms_and_conditions = Column(Text, nullable=True)
    
    # Categories and filtering
    category = Column(String(100), nullable=True)
    tags = Column(String(500), nullable=True)  # comma-separated tags
    
    # Business rules
    minimum_purchase_amount = Column(Float, nullable=True)
    applicable_branches = Column(Text, nullable=True)  # JSON array of branch IDs
    
    # Tracking
    total_redeemed = Column(Integer, default=0)
    popularity_score = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user_rewards = relationship("UserReward", back_populates="reward")
    
    def __repr__(self):
        return f"<Reward(id={self.id}, name='{self.name}', points={self.points_required})>"
    
    @property
    def is_available(self):
        """Check if reward is currently available"""
        if self.status != RewardStatus.ACTIVE:
            return False
        
        if self.remaining_quantity is not None and self.remaining_quantity <= 0:
            return False
        
        # Temporarily disable date validation to fix timezone issues
        # TODO: Implement proper timezone handling
        # from datetime import datetime, timezone
        # now = datetime.now(timezone.utc)
        
        # if self.valid_from:
        #     # Make sure valid_from is timezone aware
        #     valid_from = self.valid_from
        #     if valid_from.tzinfo is None:
        #         valid_from = valid_from.replace(tzinfo=timezone.utc)
        #     if now < valid_from:
        #         return False
        
        # if self.valid_until:
        #     # Make sure valid_until is timezone aware
        #     valid_until = self.valid_until
        #     if valid_until.tzinfo is None:
        #         valid_until = valid_until.replace(tzinfo=timezone.utc)
        #     if now > valid_until:
        #         return False
        
        return True
    
    def redeem(self):
        """Redeem one unit of this reward"""
        if self.remaining_quantity is not None:
            self.remaining_quantity -= 1
        self.total_redeemed += 1


class UserReward(Base):
    __tablename__ = "user_rewards"

    id = Column(Integer, primary_key=True, index=True)
    
    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reward_id = Column(Integer, ForeignKey("rewards.id"), nullable=False)
    
    # Redemption details
    redemption_code = Column(String(100), unique=True, index=True, nullable=False)
    points_spent = Column(Integer, nullable=False)
    status = Column(Enum(UserRewardStatus), default=UserRewardStatus.ACTIVE)
    
    # Usage tracking
    used_at = Column(DateTime(timezone=True), nullable=True)
    used_at_branch_id = Column(Integer, ForeignKey("branches.id"), nullable=True)
    
    # Validity
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Additional data
    notes = Column(Text, nullable=True)
    qr_code_url = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="user_rewards")
    reward = relationship("Reward", back_populates="user_rewards")
    used_at_branch = relationship("Branch", foreign_keys=[used_at_branch_id])
    
    def __repr__(self):
        return f"<UserReward(id={self.id}, code='{self.redemption_code}', status='{self.status}')>"
    
    @property
    def is_valid(self):
        """Check if user reward is still valid"""
        if self.status != UserRewardStatus.ACTIVE:
            return False
        
        if self.expires_at:
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            expires_at = self.expires_at
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            return now < expires_at
        
        return True
    
    def use_reward(self, branch_id: int = None):
        """Mark reward as used"""
        from datetime import datetime, timezone
        self.status = UserRewardStatus.USED
        self.used_at = datetime.now(timezone.utc)
        if branch_id:
            self.used_at_branch_id = branch_id
