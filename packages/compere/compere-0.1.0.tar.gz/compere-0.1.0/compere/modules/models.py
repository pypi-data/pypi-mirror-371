from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import List, Optional

Base = declarative_base()

class Entity(Base):
    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    image_urls = Column(String)  # Store as JSON string
    rating = Column(Float, default=1500.0)

class Comparison(Base):
    __tablename__ = "comparisons"

    id = Column(Integer, primary_key=True, index=True)
    entity1_id = Column(Integer, ForeignKey("entities.id"))
    entity2_id = Column(Integer, ForeignKey("entities.id"))
    selected_entity_id = Column(Integer, ForeignKey("entities.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Pydantic models for API responses
class EntityCreate(BaseModel):
    name: str
    description: str
    image_urls: List[str]

class EntityOut(BaseModel):
    id: int
    name: str
    description: str
    image_urls: List[str]
    rating: float

    class Config:
        from_attributes = True

class ComparisonCreate(BaseModel):
    entity1_id: int
    entity2_id: int
    selected_entity_id: int

class ComparisonOut(BaseModel):
    id: int
    entity1_id: int
    entity2_id: int
    selected_entity_id: int
    created_at: Optional[str] = None

    class Config:
        from_attributes = True
