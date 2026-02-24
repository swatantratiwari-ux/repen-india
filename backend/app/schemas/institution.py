"""
RePen India Backend — Institution Pydantic Schemas

Request and response validation schemas for the institution endpoints.
"""

import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# --- Request Schemas ---

class InstitutionRegister(BaseModel):
    """Schema for institution registration request."""
    name: str = Field(..., min_length=2, max_length=255, examples=["Delhi Public School"])
    city: str = Field(..., min_length=2, max_length=100, examples=["New Delhi"])
    email: EmailStr = Field(..., examples=["admin@dps.edu.in"])
    password: str = Field(..., min_length=8, max_length=128, examples=["SecurePass123!"])
    estimated_monthly_volume: int = Field(
        ..., ge=0, le=100000,
        description="Estimated pens collected per month",
        examples=[2000],
    )


class InstitutionLogin(BaseModel):
    """Schema for institution login request."""
    email: EmailStr = Field(..., examples=["admin@dps.edu.in"])
    password: str = Field(..., examples=["SecurePass123!"])


# --- Response Schemas ---

class InstitutionResponse(BaseModel):
    """Schema for institution profile response (no password)."""
    id: uuid.UUID
    name: str
    city: str
    email: str
    estimated_monthly_volume: int
    created_at: datetime

    model_config = {"from_attributes": True}


class InstitutionDashboard(BaseModel):
    """Aggregated dashboard data for an institution."""
    institution: InstitutionResponse
    total_collections: int
    total_weight_submitted: float
