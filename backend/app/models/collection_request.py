"""
RePen India Backend — CollectionRequest ORM Model

Represents a single pen collection pickup request
submitted by a registered institution.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class CollectionStatus(str, PyEnum):
    """Allowed statuses for a collection request."""
    PENDING = "pending"
    APPROVED = "approved"
    COMPLETED = "completed"


class CollectionRequest(Base):
    """
    ORM model for collection pickup requests.

    Fields:
        id: UUID primary key.
        institution_id: FK → institutions.id.
        estimated_weight: Weight in kilograms (float).
        pickup_address: Full address for the pickup.
        status: pending | approved | completed.
        created_at: Timestamp of request submission.
    """

    __tablename__ = "collection_requests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    institution_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("institutions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    estimated_weight: Mapped[float] = mapped_column(
        Float, nullable=False
    )
    pickup_address: Mapped[str] = mapped_column(
        String(500), nullable=False
    )
    status: Mapped[CollectionStatus] = mapped_column(
        Enum(CollectionStatus, name="collection_status", create_constraint=True),
        default=CollectionStatus.PENDING,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationship: many requests → one institution
    institution = relationship(
        "Institution",
        back_populates="collection_requests",
    )

    def __repr__(self) -> str:
        return f"<CollectionRequest {self.id} status={self.status}>"
