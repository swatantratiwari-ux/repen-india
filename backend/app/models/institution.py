"""
RePen India Backend — Institution ORM Model

Represents a registered educational institution or organisation
that participates in the pen recycling programme.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Institution(Base):
    """
    ORM model for partner institutions.

    Fields:
        id: UUID primary key (server-generated).
        name: Institution display name.
        city: City where the institution is located.
        email: Unique login email.
        hashed_password: bcrypt hash — never store plaintext.
        estimated_monthly_volume: Self-reported monthly pen estimate.
        created_at: Timestamp of registration.
    """

    __tablename__ = "institutions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    estimated_monthly_volume: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationship: one institution → many collection requests
    collection_requests = relationship(
        "CollectionRequest",
        back_populates="institution",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Institution {self.name} ({self.city})>"
