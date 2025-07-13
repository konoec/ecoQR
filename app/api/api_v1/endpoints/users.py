from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from loguru import logger

from app.core.security import get_current_active_user, get_current_admin_user
from app.db.session import get_db
from app.models.user import User
from app.models.purchase import Purchase
from app.models.recycling import RecyclingEvent
from app.schemas.user import (
    User as UserSchema,
    UserProfile,
    UserUpdate,
    UserStats,
    PasswordChange,
    UserList
)
from app.schemas.purchase import PurchaseList
from app.core.exceptions import NotFoundError, ValidationError

router = APIRouter()


@router.get("/profile", response_model=UserProfile)
async def get_user_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's profile with statistics"""
    
    # Get recent activity counts
    recent_purchases = db.query(Purchase).filter(
        Purchase.user_id == current_user.id
    ).count()
    
    recent_recycling = db.query(RecyclingEvent).filter(
        RecyclingEvent.user_id == current_user.id
    ).count()
    
    # Create response with additional data
    profile_data = {
        **current_user.__dict__,
        "full_name": current_user.full_name,
        "recent_purchases": recent_purchases,
        "recent_recycling_events": recent_recycling,
        "recent_rewards_redeemed": 0  # TODO: Implement rewards count
    }
    
    return UserProfile(**profile_data)


@router.put("/profile", response_model=UserProfile)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile"""
    
    # Update only provided fields
    update_data = user_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    logger.info(f"User profile updated: {current_user.email}")
    
    # Return updated profile
    profile_data = {
        **current_user.__dict__,
        "full_name": current_user.full_name,
    }
    
    return UserProfile(**profile_data)


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    
    from app.core.security import verify_password, get_password_hash
    
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise ValidationError("Current password is incorrect")
    
    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    
    logger.info(f"Password changed for user: {current_user.email}")
    
    return {"message": "Password changed successfully"}


@router.get("/points")
async def get_user_points(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's points balance"""
    return {
        "total_points": current_user.total_points,
        "total_recycled_items": current_user.total_recycled_items,
        "carbon_footprint_reduced": current_user.carbon_footprint_reduced
    }


@router.get("/stats", response_model=UserStats)
async def get_user_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get detailed user environmental statistics"""
    
    # Calculate recycling accuracy rate
    total_recycling = db.query(RecyclingEvent).filter(
        RecyclingEvent.user_id == current_user.id
    ).count()
    
    successful_recycling = db.query(RecyclingEvent).filter(
        RecyclingEvent.user_id == current_user.id,
        RecyclingEvent.points_earned > 0
    ).count()
    
    accuracy_rate = (successful_recycling / total_recycling * 100) if total_recycling > 0 else 0
    
    # Get monthly recycling count (current month)
    from datetime import datetime, timedelta
    current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    monthly_count = db.query(RecyclingEvent).filter(
        RecyclingEvent.user_id == current_user.id,
        RecyclingEvent.created_at >= current_month_start
    ).count()
    
    return UserStats(
        total_points=current_user.total_points,
        total_recycled_items=current_user.total_recycled_items,
        carbon_footprint_reduced=current_user.carbon_footprint_reduced,
        recycling_accuracy_rate=accuracy_rate,
        favorite_waste_categories=["plastic", "paper"],  # TODO: Calculate from data
        monthly_recycling_count=monthly_count,
        ranking_position=None  # TODO: Calculate user ranking
    )


@router.get("/purchases", response_model=List[PurchaseList])
async def get_user_purchases(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0)
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


# Admin endpoints
@router.get("/", response_model=List[UserList])
async def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None)
):
    """List all users (admin only)"""
    
    query = db.query(User)
    
    if search:
        query = query.filter(
            User.email.ilike(f"%{search}%") |
            User.first_name.ilike(f"%{search}%") |
            User.last_name.ilike(f"%{search}%")
        )
    
    users = query.order_by(User.created_at.desc()).offset(offset).limit(limit).all()
    
    result = []
    for user in users:
        result.append(UserList(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            total_points=user.total_points,
            total_recycled_items=user.total_recycled_items,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at
        ))
    
    return result


@router.get("/{user_id}", response_model=UserProfile)
async def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get user by ID (admin only)"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundError("User not found")
    
    profile_data = {
        **user.__dict__,
        "full_name": user.full_name,
    }
    
    return UserProfile(**profile_data)
