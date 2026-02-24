"""
RePen India Backend — Security Utilities

Provides:
    - Password hashing and verification (bcrypt)
    - JWT token creation and decoding (with jti + iat claims)
    - FastAPI dependency injection for protected routes
"""

import uuid
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.models.institution import Institution
from app.models.admin import Admin

settings = get_settings()

# --- Password Hashing ---
# bcrypt with automatic rounds upgrade on deprecated schemes
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against its bcrypt hash.
    passlib.verify is internally timing-safe against side-channel attacks.
    """
    return pwd_context.verify(plain_password, hashed_password)


def validate_password_strength(password: str) -> None:
    """
    Enforce password complexity requirements.
    Raises ValueError with a descriptive message on failure.
    """
    errors = []
    if len(password) < 8:
        errors.append("at least 8 characters")
    if not any(c.isupper() for c in password):
        errors.append("at least one uppercase letter")
    if not any(c.islower() for c in password):
        errors.append("at least one lowercase letter")
    if not any(c.isdigit() for c in password):
        errors.append("at least one digit")

    if errors:
        raise ValueError(f"Password must contain: {', '.join(errors)}")


# --- JWT Token ---
def create_access_token(subject: str, role: str) -> str:
    """
    Create a signed JWT access token.

    Args:
        subject: The user's email (used as 'sub' claim).
        role: Either 'institution' or 'admin'.

    Returns:
        Encoded JWT string with sub, role, exp, iat, and jti claims.
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": subject,
        "role": role,
        "exp": expire,
        "iat": now,                     # issued-at timestamp
        "jti": str(uuid.uuid4()),       # unique token ID (for future revocation)
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT access token.

    Raises HTTPException 401 if the token is invalid, expired, or malformed.
    Uses a generic error message to avoid leaking token structure details.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            options={"require_exp": True, "require_sub": True},
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# --- OAuth2 Scheme ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/institutions/login")


# --- Dependency: Get Current Institution ---
def get_current_institution(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Institution:
    """
    FastAPI dependency that extracts the current institution
    from the JWT bearer token.

    Raises HTTPException 401 if token is invalid or institution not found.
    Uses generic messages to prevent user enumeration.
    """
    payload = decode_access_token(token)

    if payload.get("role") != "institution":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    institution = db.query(Institution).filter(Institution.email == email).first()
    if institution is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    return institution


# --- Dependency: Get Current Admin ---
def get_current_admin(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Admin:
    """
    FastAPI dependency that extracts the current admin
    from the JWT bearer token.

    Raises HTTPException 401/403 if token is invalid or user is not admin.
    Uses generic messages to prevent user enumeration.
    """
    payload = decode_access_token(token)

    if payload.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    admin = db.query(Admin).filter(Admin.email == email).first()
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    return admin
