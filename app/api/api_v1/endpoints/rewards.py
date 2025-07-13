from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from loguru import logger
import uuid
from datetime import datetime, timedelta

from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.models.reward import Reward, UserReward, RewardStatus, UserRewardStatus
from app.schemas.reward import (
    Reward as RewardSchema,
    RewardList,
    RedeemRewardRequest,
    UserRewardResponse,
    UserRewardList
)
from app.services.qr_service import generate_redemption_qr
from app.core.exceptions import NotFoundError, ValidationError, BusinessLogicError

router = APIRouter()


@router.get("/", response_model=List[RewardList])
async def get_rewards_catalog(
    db: Session = Depends(get_db),
    category: str = None,
    min_points: int = None,
    max_points: int = None,
    limit: int = 20,
    offset: int = 0
):
    """Get available rewards catalog"""
    
    query = db.query(Reward).filter(Reward.status == RewardStatus.ACTIVE)
    
    if category:
        query = query.filter(Reward.category.ilike(f"%{category}%"))
    
    if min_points is not None:
        query = query.filter(Reward.points_required >= min_points)
    
    if max_points is not None:
        query = query.filter(Reward.points_required <= max_points)
    
    rewards = query.order_by(Reward.popularity_score.desc()).offset(offset).limit(limit).all()
    
    result = []
    for reward in rewards:
        result.append(RewardList(
            id=reward.id,
            name=reward.name,
            type=reward.type,
            points_required=reward.points_required,
            monetary_value=reward.monetary_value,
            image_url=reward.image_url,
            is_available=reward.is_available,
            remaining_quantity=reward.remaining_quantity,
            category=reward.category
        ))
    
    return result


@router.get("/{reward_id}", response_model=RewardSchema)
async def get_reward_details(
    reward_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific reward"""
    
    reward = db.query(Reward).filter(Reward.id == reward_id).first()
    
    if not reward:
        raise NotFoundError("Reward not found")
    
    return RewardSchema.from_orm(reward)


@router.post("/redeem", response_model=UserRewardResponse)
async def redeem_reward(
    redeem_request: RedeemRewardRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Redeem a reward using points"""
    
    # Get reward
    reward = db.query(Reward).filter(Reward.id == redeem_request.reward_id).first()
    
    if not reward:
        raise NotFoundError("Reward not found")
    
    if not reward.is_available:
        raise BusinessLogicError("Reward is not available")
    
    # Check if user has enough points
    if current_user.total_points < reward.points_required:
        raise ValidationError("Insufficient points to redeem this reward")
    
    # Check usage limit per user
    user_redemptions = db.query(UserReward).filter(
        UserReward.user_id == current_user.id,
        UserReward.reward_id == reward.id
    ).count()
    
    if user_redemptions >= reward.usage_limit_per_user:
        raise BusinessLogicError("You have reached the maximum redemptions for this reward")
    
    # Generate redemption code
    redemption_code = f"RWD-{uuid.uuid4().hex[:10].upper()}"
    
    # Calculate expiry date (30 days from now)
    expires_at = datetime.utcnow() + timedelta(days=30)
    
    # Create user reward
    user_reward = UserReward(
        user_id=current_user.id,
        reward_id=reward.id,
        redemption_code=redemption_code,
        points_spent=reward.points_required,
        status=UserRewardStatus.ACTIVE,
        expires_at=expires_at,
        notes=redeem_request.notes
    )
    
    db.add(user_reward)
    db.flush()
    
    # Generate QR code for redemption
    qr_data = {
        "user_id": current_user.id,
        "reward_id": reward.id,
        "reward_name": reward.name,
        "expires_at": expires_at.isoformat()
    }
    
    qr_code_url = await generate_redemption_qr(redemption_code, qr_data)
    user_reward.qr_code_url = qr_code_url
    
    # Deduct points from user
    current_user.subtract_points(reward.points_required)
    
    # Update reward statistics
    reward.redeem()
    
    db.commit()
    db.refresh(user_reward)
    
    logger.info(
        f"Reward redeemed: {redemption_code} - "
        f"User: {current_user.email} - "
        f"Reward: {reward.name} - "
        f"Points: {reward.points_required}"
    )
    
    # Build response
    response_data = {
        **user_reward.__dict__,
        "reward": {
            "id": reward.id,
            "name": reward.name,
            "type": reward.type,
            "description": reward.description,
            "terms_and_conditions": reward.terms_and_conditions
        }
    }
    
    return UserRewardResponse(**response_data)


@router.get("/user/my-rewards", response_model=List[UserRewardList])
async def get_user_rewards(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    status_filter: UserRewardStatus = None,
    limit: int = 20,
    offset: int = 0
):
    """Get user's redeemed rewards"""
    
    query = db.query(UserReward).filter(UserReward.user_id == current_user.id)
    
    if status_filter:
        query = query.filter(UserReward.status == status_filter)
    
    user_rewards = query.order_by(UserReward.created_at.desc()).offset(offset).limit(limit).all()
    
    result = []
    for user_reward in user_rewards:
        result.append(UserRewardList(
            id=user_reward.id,
            redemption_code=user_reward.redemption_code,
            status=user_reward.status,
            points_spent=user_reward.points_spent,
            expires_at=user_reward.expires_at,
            created_at=user_reward.created_at,
            reward_name=user_reward.reward.name,
            reward_type=user_reward.reward.type,
            is_valid=user_reward.is_valid
        ))
    
    return result


@router.get("/user/my-rewards/{reward_id}", response_model=UserRewardResponse)
async def get_user_reward_details(
    reward_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a user's specific reward"""
    
    user_reward = db.query(UserReward).filter(
        UserReward.id == reward_id,
        UserReward.user_id == current_user.id
    ).first()
    
    if not user_reward:
        raise NotFoundError("User reward not found")
    
    # Build response with related data
    response_data = {
        **user_reward.__dict__,
        "reward": {
            "id": user_reward.reward.id,
            "name": user_reward.reward.name,
            "type": user_reward.reward.type,
            "description": user_reward.reward.description,
            "terms_and_conditions": user_reward.reward.terms_and_conditions,
            "image_url": user_reward.reward.image_url
        }
    }
    
    return UserRewardResponse(**response_data)


@router.post("/user/my-rewards/{reward_id}/use")
async def use_reward(
    reward_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    branch_id: int = None
):
    """Mark a reward as used (typically called by branch staff)"""
    
    user_reward = db.query(UserReward).filter(
        UserReward.id == reward_id,
        UserReward.user_id == current_user.id
    ).first()
    
    if not user_reward:
        raise NotFoundError("User reward not found")
    
    if not user_reward.is_valid:
        raise BusinessLogicError("Reward is not valid or has expired")
    
    if user_reward.status != UserRewardStatus.ACTIVE:
        raise BusinessLogicError("Reward has already been used or is not active")
    
    # Mark as used
    user_reward.use_reward(branch_id)
    db.commit()
    
    logger.info(f"Reward used: {user_reward.redemption_code} by user {current_user.email}")
    
    return {
        "message": "Reward used successfully",
        "redemption_code": user_reward.redemption_code,
        "used_at": user_reward.used_at
    }
