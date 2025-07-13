from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import enum
import json


class RecyclingStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ValidationStatus(str, enum.Enum):
    PENDING = "pending"
    VALIDATED = "validated"
    REJECTED = "rejected"
    MANUAL_REVIEW = "manual_review"


class RecyclingEvent(Base):
    __tablename__ = "recycling_events"

    id = Column(Integer, primary_key=True, index=True)
    
    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    purchase_id = Column(Integer, ForeignKey("purchases.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    
    # Event details
    event_code = Column(String(100), unique=True, index=True, nullable=False)
    status = Column(Enum(RecyclingStatus), default=RecyclingStatus.PENDING)
    validation_status = Column(Enum(ValidationStatus), default=ValidationStatus.PENDING)
    
    # Points and rewards
    points_earned = Column(Integer, default=0)
    points_potential = Column(Integer, default=0)
    accuracy_score = Column(Float, default=0.0)  # 0-100
    
    # AI Validation
    ai_validation_id = Column(String(100), nullable=True)
    ai_confidence_score = Column(Float, default=0.0)
    validation_image_url = Column(String(500), nullable=True)
    validation_metadata = Column(Text, nullable=True)  # JSON with validation details
    
    # Environmental impact
    total_weight_recycled = Column(Float, default=0.0)  # in kg
    carbon_footprint_reduced = Column(Float, default=0.0)  # in kg CO2
    
    # Process tracking
    qr_scanned_at = Column(DateTime(timezone=True), nullable=True)
    validation_started_at = Column(DateTime(timezone=True), nullable=True)
    validation_completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="recycling_events")
    purchase = relationship("Purchase", back_populates="recycling_events")
    branch = relationship("Branch", back_populates="recycling_events")
    items = relationship("RecyclingItem", back_populates="recycling_event", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<RecyclingEvent(id={self.id}, code='{self.event_code}', status='{self.status}')>"
    
    @property
    def validation_metadata_dict(self):
        """Get validation metadata as dictionary"""
        if self.validation_metadata:
            return json.loads(self.validation_metadata)
        return {}
    
    def set_validation_metadata(self, data: dict):
        """Set validation metadata from dictionary"""
        self.validation_metadata = json.dumps(data)
    
    def calculate_points(self):
        """Calculate points based on recycled items and accuracy"""
        base_points = sum(item.points_awarded for item in self.items)
        accuracy_multiplier = self.accuracy_score / 100.0
        self.points_earned = int(base_points * accuracy_multiplier)
    
    def calculate_environmental_impact(self):
        """Calculate environmental impact"""
        self.total_weight_recycled = sum(item.weight_recycled for item in self.items)
        self.carbon_footprint_reduced = sum(
            item.weight_recycled * item.waste_type.carbon_footprint_per_kg 
            for item in self.items
        )


class RecyclingItem(Base):
    __tablename__ = "recycling_items"

    id = Column(Integer, primary_key=True, index=True)
    
    # Relationships
    recycling_event_id = Column(Integer, ForeignKey("recycling_events.id"), nullable=False)
    waste_type_id = Column(Integer, ForeignKey("waste_types.id"), nullable=False)
    
    # Item details
    name = Column(String(200), nullable=False)
    quantity = Column(Integer, default=1)
    weight_recycled = Column(Float, default=0.0)  # in kg
    
    # Classification results
    is_correctly_classified = Column(Boolean, default=False)
    predicted_bin = Column(String(50), nullable=True)
    actual_bin = Column(String(50), nullable=True)
    confidence_score = Column(Float, default=0.0)
    
    # Points
    points_potential = Column(Integer, default=0)
    points_awarded = Column(Integer, default=0)
    
    # Validation details
    validation_notes = Column(Text, nullable=True)
    rejected_reason = Column(String(200), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    recycling_event = relationship("RecyclingEvent", back_populates="items")
    waste_type = relationship("WasteType", back_populates="recycling_items")
    
    def __repr__(self):
        return f"<RecyclingItem(id={self.id}, name='{self.name}', correctly_classified={self.is_correctly_classified})>"
