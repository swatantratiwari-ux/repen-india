"""
RePen India Backend — Admin ORM Model

Represents a platform administrator who can manage
institutions and update collection request statuses.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Admin(Base):
    """
    ORM model for platform administrators.

    Fields:
        id: UUID primary key.
        email: Unique admin email (login identifier).
        hashed_password: bcrypt hash.
        created_at: Timestamp.
    """

    __tablename__ = "admins"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Admin {self.email}>"
