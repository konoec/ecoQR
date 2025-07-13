from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime


class EnvironmentalStats(BaseModel):
    """Environmental impact statistics"""
    total_waste_recycled: float  # in kg
    carbon_footprint_reduced: float  # in kg CO2
    recycling_accuracy_rate: float  # percentage
    total_recycling_events: int
    active_users: int
    total_points_awarded: int


class BranchRanking(BaseModel):
    """Branch ranking information"""
    branch_id: int
    branch_name: str
    branch_city: str
    total_recycled_items: int
    carbon_footprint_reduced: float
    recycling_accuracy_rate: float
    active_users_count: int
    rank: int


class UserRanking(BaseModel):
    """User ranking information"""
    user_id: int
    user_name: str
    total_points: int
    total_recycled_items: int
    carbon_footprint_reduced: float
    recycling_accuracy_rate: float
    rank: int


class WasteCategoryStats(BaseModel):
    """Statistics by waste category"""
    category: str
    total_items: int
    total_weight: float
    carbon_reduction: float
    accuracy_rate: float
    points_awarded: int


class MonthlyTrend(BaseModel):
    """Monthly trend data"""
    month: str  # YYYY-MM
    recycling_events: int
    weight_recycled: float
    carbon_reduced: float
    new_users: int
    accuracy_rate: float


class AdminDashboard(BaseModel):
    """Complete admin dashboard data"""
    overview: EnvironmentalStats
    top_branches: List[BranchRanking]
    top_users: List[UserRanking]
    waste_categories: List[WasteCategoryStats]
    monthly_trends: List[MonthlyTrend]
    recent_activities: List[Dict[str, Any]]


class UserActivityLog(BaseModel):
    """User activity log entry"""
    id: int
    user_id: int
    user_name: str
    activity_type: str
    description: str
    points_change: Optional[int]
    timestamp: datetime
    branch_name: Optional[str]


class SystemHealth(BaseModel):
    """System health metrics"""
    database_status: str
    api_response_time: float
    active_sessions: int
    error_rate: float
    uptime: str
    last_backup: datetime


class ReportRequest(BaseModel):
    """Request for generating reports"""
    report_type: str  # "environmental", "users", "branches", "rewards"
    date_from: datetime
    date_to: datetime
    branch_ids: Optional[List[int]] = None
    format: str = "json"  # "json", "csv", "pdf"


class BulkUserUpdate(BaseModel):
    """Bulk user update request"""
    user_ids: List[int]
    updates: Dict[str, Any]


class BulkActionResponse(BaseModel):
    """Response for bulk actions"""
    success: bool
    affected_count: int
    errors: List[Dict[str, Any]]
    message: str
