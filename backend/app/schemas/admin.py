"""
RePen India Backend — Admin Pydantic Schemas

Request and response schemas for admin endpoints.
"""

import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# --- Request Schemas ---

class AdminLogin(BaseModel):
    """Schema for admin login request."""
    email: EmailStr = Field(..., examples=["admin@repenindia.in"])
    password: str = Field(..., examples=["AdminSecure123!"])


class AdminCreate(BaseModel):
    """Schema for creating a new admin (internal use only)."""
    email: EmailStr = Field(..., examples=["admin@repenindia.in"])
    password: str = Field(..., min_length=8, max_length=128)


# --- Response Schemas ---

class AdminResponse(BaseModel):
    """Schema for admin profile response."""
    id: uuid.UUID
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}
