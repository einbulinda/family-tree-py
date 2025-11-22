from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime


# Allowed relationship types
class RelationshipType(str, Enum):
    parent = "parent"
    child = "child"
    spouse = "spouse"
    sibling = "sibling"


class RelationshipBase(BaseModel):
    individual_id: int = Field(..., description="The main individual")
    related_individual_id: int = Field(..., description="The related individual")
    relationship_type: RelationshipType = Field(
        ..., description="Type of relationship: parent, child, spouse, sibling"
    )


class RelationshipCreate(RelationshipBase):
    """Schema for creating a relationship"""
    pass


class RelationshipUpdate(BaseModel):
    """Optional update fields"""
    relationship_type: Optional[RelationshipType] = None


class RelationshipResponse(RelationshipBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
