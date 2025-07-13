from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=True)
    
    # Location coordinates
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Contact information
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    manager_name = Column(String(200), nullable=True)
    
    # Branch status
    is_active = Column(Boolean, default=True)
    
    # Environmental metrics
    total_recycled_items = Column(Integer, default=0)
    total_carbon_reduced = Column(Float, default=0.0)  # in kg CO2
    recycling_accuracy_rate = Column(Float, default=0.0)  # percentage
    
    # Operating hours (can be extended to a separate table if needed)
    opening_hours = Column(Text, nullable=True)  # JSON string with daily hours
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    purchases = relationship("Purchase", back_populates="branch")
    recycling_events = relationship("RecyclingEvent", back_populates="branch")
    
    def __repr__(self):
        return f"<Branch(id={self.id}, name='{self.name}', city='{self.city}')>"
    
    @property
    def full_address(self):
        """Get complete formatted address"""
        return f"{self.address}, {self.city}, {self.state}, {self.country}"
    
    def update_recycling_stats(self, items_count: int, carbon_reduced: float):
        """Update branch recycling statistics"""
        self.total_recycled_items += items_count
        self.total_carbon_reduced += carbon_reduced
