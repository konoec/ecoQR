from fastapi import APIRouter
from app.api.api_v1.endpoints import (
    auth,
    users,
    purchases,
    recycling,
    rewards,
    branches,
    admin,
    ai_validation
)

api_router = APIRouter()

# Authentication routes
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# User routes  
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Purchase routes
api_router.include_router(purchases.router, prefix="/purchases", tags=["purchases"])

# Recycling routes
api_router.include_router(recycling.router, prefix="/recycling", tags=["recycling"])

# Rewards routes
api_router.include_router(rewards.router, prefix="/rewards", tags=["rewards"])

# Branches routes
api_router.include_router(branches.router, prefix="/branches", tags=["branches"])

# Admin routes
api_router.include_router(admin.router, prefix="/admin", tags=["administration"])

# AI Validation routes
api_router.include_router(ai_validation.router, prefix="/ai", tags=["ai-validation"])
