"""
RePen India Backend — CollectionRequest Pydantic Schemas

Request and response validation for collection request endpoints.
"""

import uuid
from datetime import datetime
from pydantic import BaseModel, Field

from app.models.collection_request import CollectionStatus


# --- Request Schemas ---

class CollectionRequestCreate(BaseModel):
    """Schema for creating a new collection pickup request."""
    estimated_weight: float = Field(
        ..., gt=0, le=50000,
        description="Estimated weight in kilograms",
        examples=[12.5],
    )
    pickup_address: str = Field(
        ..., min_length=10, max_length=500,
        examples=["Block A, Delhi Public School, Mathura Road, New Delhi 110003"],
    )


class CollectionStatusUpdate(BaseModel):
    """Schema for admin updating a collection request status."""
    status: CollectionStatus = Field(
        ..., examples=["approved"],
    )


# --- Response Schemas ---

class CollectionRequestResponse(BaseModel):
    """Schema for a single collection request response."""
    id: uuid.UUID
    institution_id: uuid.UUID
    estimated_weight: float
    pickup_address: str
    status: CollectionStatus
    created_at: datetime

    model_config = {"from_attributes": True}
