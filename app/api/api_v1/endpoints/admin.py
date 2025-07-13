from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from loguru import logger
from datetime import datetime, timedelta

from app.core.security import get_current_admin_user
from app.db.session import get_db
from app.models.user import User
from app.models.branch import Branch
from app.models.recycling import RecyclingEvent
from app.models.purchase import Purchase
from app.schemas.admin import (
    AdminDashboard,
    EnvironmentalStats,
    BranchRanking,
    UserRanking,
    WasteCategoryStats,
    MonthlyTrend
)

router = APIRouter()


@router.get("/dashboard", response_model=AdminDashboard)
async def get_admin_dashboard(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get complete admin dashboard data"""
    
    # Calculate overview statistics
    total_recycling_events = db.query(RecyclingEvent).count()
    total_users = db.query(User).filter(User.is_active == True).count()
    total_branches = db.query(Branch).filter(Branch.is_active == True).count()
    
    # Calculate environmental stats
    total_waste = db.query(RecyclingEvent).with_entities(
        func.sum(RecyclingEvent.total_weight_recycled)
    ).scalar() or 0.0
    
    total_carbon = db.query(RecyclingEvent).with_entities(
        func.sum(RecyclingEvent.carbon_footprint_reduced)
    ).scalar() or 0.0
    
    total_points = db.query(RecyclingEvent).with_entities(
        func.sum(RecyclingEvent.points_earned)
    ).scalar() or 0
    
    avg_accuracy = db.query(RecyclingEvent).with_entities(
        func.avg(RecyclingEvent.accuracy_score)
    ).scalar() or 0.0
    
    overview = EnvironmentalStats(
        total_waste_recycled=total_waste,
        carbon_footprint_reduced=total_carbon,
        recycling_accuracy_rate=avg_accuracy,
        total_recycling_events=total_recycling_events,
        active_users=total_users,
        total_points_awarded=total_points
    )
    
    # Get top branches
    branches = db.query(Branch).filter(Branch.is_active == True).order_by(
        Branch.total_recycled_items.desc()
    ).limit(10).all()
    
    top_branches = []
    for i, branch in enumerate(branches, 1):
        top_branches.append(BranchRanking(
            branch_id=branch.id,
            branch_name=branch.name,
            branch_city=branch.city,
            total_recycled_items=branch.total_recycled_items,
            carbon_footprint_reduced=branch.total_carbon_reduced,
            recycling_accuracy_rate=branch.recycling_accuracy_rate,
            active_users_count=50,  # Mock data
            rank=i
        ))
    
    # Get top users
    users = db.query(User).filter(User.is_active == True).order_by(
        User.total_points.desc()
    ).limit(10).all()
    
    top_users = []
    for i, user in enumerate(users, 1):
        top_users.append(UserRanking(
            user_id=user.id,
            user_name=user.full_name,
            total_points=user.total_points,
            total_recycled_items=user.total_recycled_items,
            carbon_footprint_reduced=user.carbon_footprint_reduced,
            recycling_accuracy_rate=85.0,  # Mock data
            rank=i
        ))
    
    # Mock waste categories data
    waste_categories = [
        WasteCategoryStats(
            category="plastic",
            total_items=1250,
            total_weight=125.5,
            carbon_reduction=45.2,
            accuracy_rate=87.5,
            points_awarded=12500
        ),
        WasteCategoryStats(
            category="paper",
            total_items=980,
            total_weight=98.0,
            carbon_reduction=35.1,
            accuracy_rate=92.3,
            points_awarded=9800
        ),
        WasteCategoryStats(
            category="glass",
            total_items=650,
            total_weight=195.0,
            carbon_reduction=58.5,
            accuracy_rate=94.1,
            points_awarded=6500
        )
    ]
    
    # Generate monthly trends for last 6 months
    monthly_trends = []
    for i in range(6):
        month_date = datetime.utcnow() - timedelta(days=30 * i)
        monthly_trends.append(MonthlyTrend(
            month=month_date.strftime("%Y-%m"),
            recycling_events=150 + i * 20,
            weight_recycled=45.5 + i * 5.2,
            carbon_reduced=16.8 + i * 1.9,
            new_users=25 + i * 3,
            accuracy_rate=85.0 + i * 1.5
        ))
    
    monthly_trends.reverse()  # Most recent first
    
    # Recent activities (mock data)
    recent_activities = [
        {
            "type": "recycling",
            "description": "User completed recycling with 95% accuracy",
            "timestamp": datetime.utcnow() - timedelta(minutes=15),
            "points": 150
        },
        {
            "type": "reward_redemption", 
            "description": "User redeemed coffee voucher",
            "timestamp": datetime.utcnow() - timedelta(hours=2),
            "points": -500
        },
        {
            "type": "new_user",
            "description": "New user registered",
            "timestamp": datetime.utcnow() - timedelta(hours=4),
            "points": 0
        }
    ]
    
    return AdminDashboard(
        overview=overview,
        top_branches=top_branches,
        top_users=top_users,
        waste_categories=waste_categories,
        monthly_trends=monthly_trends,
        recent_activities=recent_activities
    )


@router.get("/stats/environmental")
async def get_environmental_stats(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
    days: int = 30
):
    """Get detailed environmental impact statistics"""
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Query recycling events in the period
    events = db.query(RecyclingEvent).filter(
        RecyclingEvent.created_at >= cutoff_date
    ).all()
    
    total_events = len(events)
    total_weight = sum(event.total_weight_recycled for event in events)
    total_carbon = sum(event.carbon_footprint_reduced for event in events)
    total_points = sum(event.points_earned for event in events)
    
    avg_accuracy = sum(event.accuracy_score for event in events) / total_events if total_events > 0 else 0
    
    # Calculate by category
    category_stats = {}
    for event in events:
        for item in event.items:
            category = item.waste_type.category
            if category not in category_stats:
                category_stats[category] = {
                    "items": 0,
                    "weight": 0.0,
                    "carbon": 0.0,
                    "points": 0
                }
            
            category_stats[category]["items"] += 1
            category_stats[category]["weight"] += item.weight_recycled
            category_stats[category]["carbon"] += item.weight_recycled * item.waste_type.carbon_footprint_per_kg
            category_stats[category]["points"] += item.points_awarded
    
    return {
        "period_days": days,
        "total_events": total_events,
        "total_weight_kg": total_weight,
        "total_carbon_reduced_kg": total_carbon,
        "total_points_awarded": total_points,
        "average_accuracy": avg_accuracy,
        "category_breakdown": category_stats,
        "daily_average": {
            "events": total_events / days,
            "weight_kg": total_weight / days,
            "carbon_kg": total_carbon / days
        }
    }


@router.get("/stats/users")
async def get_user_statistics(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get user engagement and activity statistics"""
    
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    verified_users = db.query(User).filter(User.is_verified == True).count()
    
    # Users by registration date (last 6 months)
    monthly_registrations = []
    for i in range(6):
        month_start = (datetime.utcnow() - timedelta(days=30 * (i + 1))).replace(day=1)
        month_end = (datetime.utcnow() - timedelta(days=30 * i)).replace(day=1)
        
        count = db.query(User).filter(
            User.created_at >= month_start,
            User.created_at < month_end
        ).count()
        
        monthly_registrations.append({
            "month": month_start.strftime("%Y-%m"),
            "registrations": count
        })
    
    # Top users by points
    top_users = db.query(User).filter(User.is_active == True).order_by(
        User.total_points.desc()
    ).limit(20).all()
    
    user_rankings = []
    for i, user in enumerate(top_users, 1):
        user_rankings.append({
            "rank": i,
            "user_id": user.id,
            "name": user.full_name,
            "email": user.email,
            "total_points": user.total_points,
            "recycled_items": user.total_recycled_items,
            "carbon_reduced": user.carbon_footprint_reduced
        })
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "verified_users": verified_users,
        "verification_rate": (verified_users / total_users * 100) if total_users > 0 else 0,
        "monthly_registrations": monthly_registrations,
        "top_users": user_rankings
    }


@router.get("/stats/branches")
async def get_branch_statistics(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get branch performance statistics"""
    
    branches = db.query(Branch).filter(Branch.is_active == True).all()
    
    branch_stats = []
    for branch in branches:
        # Count events for this branch
        events_count = db.query(RecyclingEvent).filter(
            RecyclingEvent.branch_id == branch.id
        ).count()
        
        # Count unique users
        unique_users = db.query(RecyclingEvent.user_id).filter(
            RecyclingEvent.branch_id == branch.id
        ).distinct().count()
        
        branch_stats.append({
            "branch_id": branch.id,
            "name": branch.name,
            "city": branch.city,
            "total_recycled_items": branch.total_recycled_items,
            "carbon_reduced": branch.total_carbon_reduced,
            "accuracy_rate": branch.recycling_accuracy_rate,
            "total_events": events_count,
            "unique_users": unique_users
        })
    
    # Sort by performance score (combination of metrics)
    branch_stats.sort(key=lambda x: x["total_recycled_items"], reverse=True)
    
    return {
        "total_branches": len(branch_stats),
        "branch_rankings": branch_stats
    }
