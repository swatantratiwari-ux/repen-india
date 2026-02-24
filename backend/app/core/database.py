"""
RePen India Backend — Database Session Management

Provides the SQLAlchemy engine, session factory,
and a dependency-injectable get_db generator for route handlers.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase

from app.core.config import get_settings

settings = get_settings()

# --- Engine ---
# pool_pre_ping: recycle stale connections
# pool_size / max_overflow: prevent unbounded connection growth
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    echo=(settings.app_env == "development"),
)

# --- Session Factory ---
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


# --- Declarative Base ---
class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


# --- Dependency ---
def get_db() -> Session:
    """
    FastAPI dependency that yields a database session.
    Automatically closes the session when the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
