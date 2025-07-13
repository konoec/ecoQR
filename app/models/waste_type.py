from sqlalchemy import Column, Integer, String, Float, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from app.db.session import Base


class WasteType(Base):
    __tablename__ = "waste_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False)  # organic, plastic, paper, glass, metal, electronic
    
    # Environmental impact metrics
    recycling_points = Column(Integer, default=0)  # Points awarded for recycling
    carbon_footprint_per_kg = Column(Float, default=0.0)  # kg CO2 per kg of waste
    biodegradable = Column(Boolean, default=False)
    
    # Recycling information
    recycling_instructions = Column(Text, nullable=True)
    bin_color = Column(String(50), nullable=True)  # Color of the recycling bin
    processing_difficulty = Column(String(20), default="medium")  # easy, medium, hard
    
    # Visual identification
    icon_url = Column(String(500), nullable=True)
    color_hex = Column(String(7), nullable=True)  # Color for UI display
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    purchase_items = relationship("PurchaseItem", back_populates="waste_type")
    recycling_items = relationship("RecyclingItem", back_populates="waste_type")
    
    def __repr__(self):
        return f"<WasteType(id={self.id}, name='{self.name}', category='{self.category}')>"
    
    @property
    def difficulty_score(self):
        """Get numeric difficulty score"""
        difficulty_map = {"easy": 1, "medium": 2, "hard": 3}
        return difficulty_map.get(self.processing_difficulty, 2)
