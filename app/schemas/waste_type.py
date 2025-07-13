from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class WasteTypeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    category: str = Field(..., max_length=50)
    recycling_points: int = Field(0, ge=0)
    carbon_footprint_per_kg: float = Field(0.0, ge=0)
    biodegradable: bool = False
    recycling_instructions: Optional[str] = None
    bin_color: Optional[str] = Field(None, max_length=50)
    processing_difficulty: str = Field("medium", pattern="^(easy|medium|hard)$")
    icon_url: Optional[str] = Field(None, max_length=500)
    color_hex: Optional[str] = Field(None, max_length=7)


class WasteTypeCreate(WasteTypeBase):
    pass


class WasteTypeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)
    recycling_points: Optional[int] = Field(None, ge=0)
    carbon_footprint_per_kg: Optional[float] = Field(None, ge=0)
    biodegradable: Optional[bool] = None
    recycling_instructions: Optional[str] = None
    bin_color: Optional[str] = Field(None, max_length=50)
    processing_difficulty: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")
    icon_url: Optional[str] = Field(None, max_length=500)
    color_hex: Optional[str] = Field(None, max_length=7)
    is_active: Optional[bool] = None


class WasteType(WasteTypeBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class WasteTypeList(BaseModel):
    id: int
    name: str
    category: str
    recycling_points: int
    bin_color: Optional[str]
    is_active: bool
    
    class Config:
        from_attributes = True
