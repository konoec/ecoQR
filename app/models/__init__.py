# Import all models to ensure they are registered
from .user import User
from .branch import Branch
from .waste_type import WasteType
from .purchase import Purchase
from .recycling import RecyclingEvent
from .reward import Reward, UserReward

__all__ = [
    "User",
    "Branch", 
    "WasteType",
    "Purchase",
    "RecyclingEvent",
    "Reward",
    "UserReward"
]
