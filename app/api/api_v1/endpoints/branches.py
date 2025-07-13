from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from loguru import logger

from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.models.branch import Branch
from app.schemas.branch import Branch as BranchSchema, BranchList, BranchStats

router = APIRouter()


@router.get("/", response_model=List[BranchList])
async def get_branches(
    db: Session = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
    city: str = None
):
    """Get list of active branches"""
    
    query = db.query(Branch).filter(Branch.is_active == True)
    
    if city:
        query = query.filter(Branch.city.ilike(f"%{city}%"))
    
    branches = query.order_by(Branch.name).offset(offset).limit(limit).all()
    
    result = []
    for branch in branches:
        result.append(BranchList(
            id=branch.id,
            name=branch.name,
            city=branch.city,
            state=branch.state,
            country=branch.country,
            is_active=branch.is_active,
            total_recycled_items=branch.total_recycled_items
        ))
    
    return result


@router.get("/{branch_id}", response_model=BranchSchema)
async def get_branch_details(
    branch_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific branch"""
    
    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Branch not found"
        )
    
    return BranchSchema.from_orm(branch)


@router.get("/{branch_id}/stats", response_model=BranchStats)
async def get_branch_stats(
    branch_id: int,
    db: Session = Depends(get_db)
):
    """Get environmental statistics for a specific branch"""
    
    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Branch not found"
        )
    
    # Calculate monthly recycling count
    from datetime import datetime, timedelta
    from app.models.recycling import RecyclingEvent
    
    current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    monthly_count = db.query(RecyclingEvent).filter(
        RecyclingEvent.branch_id == branch_id,
        RecyclingEvent.created_at >= current_month_start
    ).count()
    
    # Get most recycled categories (mock data for now)
    most_recycled_categories = [
        {"category": "plastic", "count": 150, "percentage": 35},
        {"category": "paper", "count": 120, "percentage": 28},
        {"category": "glass", "count": 80, "percentage": 19},
        {"category": "metal", "count": 50, "percentage": 12},
        {"category": "organic", "count": 25, "percentage": 6}
    ]
    
    # Get top users (mock data for now)
    top_users = [
        {"user_name": "Maria Rodriguez", "points": 1250, "recycled_items": 85},
        {"user_name": "Carlos Silva", "points": 980, "recycled_items": 67},
        {"user_name": "Ana Lopez", "points": 875, "recycled_items": 54}
    ]
    
    return BranchStats(
        id=branch.id,
        name=branch.name,
        total_recycled_items=branch.total_recycled_items,
        total_carbon_reduced=branch.total_carbon_reduced,
        recycling_accuracy_rate=branch.recycling_accuracy_rate,
        monthly_recycling_count=monthly_count,
        most_recycled_categories=most_recycled_categories,
        top_users=top_users
    )
