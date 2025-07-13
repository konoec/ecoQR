from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import uuid
import json


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    purchase_code = Column(String(100), unique=True, index=True, nullable=False)
    
    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    
    # Purchase details
    total_amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    payment_method = Column(String(50), nullable=True)
    
    # Environmental impact
    estimated_waste_weight = Column(Float, default=0.0)  # in kg
    potential_points = Column(Integer, default=0)
    environmental_impact_score = Column(Float, default=0.0)
    
    # QR Code
    qr_code_data = Column(Text, nullable=True)  # JSON with QR data
    qr_code_url = Column(String(500), nullable=True)
    qr_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    is_recycled = Column(Boolean, default=False)
    recycled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="purchases")
    branch = relationship("Branch", back_populates="purchases")
    items = relationship("PurchaseItem", back_populates="purchase", cascade="all, delete-orphan")
    recycling_events = relationship("RecyclingEvent", back_populates="purchase")
    
    def __repr__(self):
        return f"<Purchase(id={self.id}, code='{self.purchase_code}', amount={self.total_amount})>"
    
    @property
    def qr_data_dict(self):
        """Get QR code data as dictionary"""
        if self.qr_code_data:
            return json.loads(self.qr_code_data)
        return {}
    
    def set_qr_data(self, data: dict):
        """Set QR code data from dictionary"""
        self.qr_code_data = json.dumps(data)
    
    def calculate_environmental_impact(self):
        """Calculate environmental impact based on items"""
        total_weight = sum(item.estimated_weight for item in self.items)
        total_points = sum(item.potential_points for item in self.items)
        
        self.estimated_waste_weight = total_weight
        self.potential_points = total_points
        
        # Calculate impact score (can be customized based on business logic)
        self.environmental_impact_score = total_weight * 0.5 + total_points * 0.1


class PurchaseItem(Base):
    __tablename__ = "purchase_items"

    id = Column(Integer, primary_key=True, index=True)
    
    # Relationships
    purchase_id = Column(Integer, ForeignKey("purchases.id"), nullable=False)
    waste_type_id = Column(Integer, ForeignKey("waste_types.id"), nullable=False)
    
    # Item details
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, nullable=True)
    
    # Environmental data
    estimated_weight = Column(Float, default=0.0)  # in kg
    potential_points = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    purchase = relationship("Purchase", back_populates="items")
    waste_type = relationship("WasteType", back_populates="purchase_items")
    
    def __repr__(self):
        return f"<PurchaseItem(id={self.id}, name='{self.name}', quantity={self.quantity})>"
