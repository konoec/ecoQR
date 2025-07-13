from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    
    # User status and roles
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    
    # Environmental tracking
    total_points = Column(Integer, default=0)
    total_recycled_items = Column(Integer, default=0)
    carbon_footprint_reduced = Column(Float, default=0.0)  # in kg CO2
    
    # Profile information
    profile_image_url = Column(String(500), nullable=True)
    preferred_language = Column(String(5), default="es")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    purchases = relationship("Purchase", back_populates="user")
    recycling_events = relationship("RecyclingEvent", back_populates="user")
    user_rewards = relationship("UserReward", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', points={self.total_points})>"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def add_points(self, points: int):
        """Add points to user's total"""
        self.total_points += points
    
    def subtract_points(self, points: int) -> bool:
        """Subtract points from user's total, return False if insufficient points"""
        if self.total_points >= points:
            self.total_points -= points
            return True
        return False
