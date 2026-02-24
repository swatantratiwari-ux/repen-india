"""
RePen India Backend — Shared Token Schema

Reusable JWT response schema.
"""

from pydantic import BaseModel


class TokenResponse(BaseModel):
    """Schema returned after successful authentication."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Decoded JWT payload data."""
    sub: str  # subject (email)
    role: str  # "institution" or "admin"
