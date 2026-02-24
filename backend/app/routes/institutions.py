"""
RePen India Backend — Institution Routes

Endpoints:
    POST /register — Register a new institution
    POST /login    — Authenticate and receive JWT
    GET  /me       — Fetch current institution profile (protected)
    GET  /dashboard — Aggregated dashboard data (protected)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.security import (
    hash_password,
    verify_password,
    validate_password_strength,
    create_access_token,
    get_current_institution,
)
from app.models.institution import Institution
from app.models.collection_request import CollectionRequest
from app.schemas.institution import (
    InstitutionRegister,
    InstitutionLogin,
    InstitutionResponse,
    InstitutionDashboard,
)
from app.schemas.token import TokenResponse

router = APIRouter(prefix="/institutions", tags=["Institutions"])


# --- Register ---
@router.post(
    "/register",
    response_model=InstitutionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new institution",
)
def register_institution(
    data: InstitutionRegister,
    db: Session = Depends(get_db),
):
    """
    Create a new institution account.
    Email must be unique — returns 409 if already taken.
    Password is validated for strength, then hashed with bcrypt.
    """
    # Validate password strength before hashing
    try:
        validate_password_strength(data.password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    # Check for duplicate email
    existing = db.query(Institution).filter(Institution.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Registration could not be completed",
        )

    institution = Institution(
        name=data.name,
        city=data.city,
        email=data.email,
        hashed_password=hash_password(data.password),
        estimated_monthly_volume=data.estimated_monthly_volume,
    )
    db.add(institution)
    db.commit()
    db.refresh(institution)

    return institution


# --- Login ---
@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate an institution",
)
def login_institution(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Verify credentials and return a JWT access token.
    Returns 401 if email or password is incorrect.
    """
    email = form_data.username
    password = form_data.password

    institution = db.query(Institution).filter(Institution.email == email).first()

    if not institution or not verify_password(password, institution.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    token = create_access_token(subject=institution.email, role="institution")
    return TokenResponse(access_token=token)


# --- Profile ---
@router.get(
    "/me",
    response_model=InstitutionResponse,
    summary="Get current institution profile",
)
def get_profile(
    current: Institution = Depends(get_current_institution),
):
    """Return the authenticated institution's profile data."""
    return current


# --- Dashboard ---
@router.get(
    "/dashboard",
    response_model=InstitutionDashboard,
    summary="Get institution dashboard",
)
def get_dashboard(
    current: Institution = Depends(get_current_institution),
    db: Session = Depends(get_db),
):
    """
    Return aggregated dashboard data:
    - Institution profile
    - Total number of collection requests
    - Total weight submitted across all collections
    """
    total_collections = (
        db.query(func.count(CollectionRequest.id))
        .filter(CollectionRequest.institution_id == current.id)
        .scalar()
    )

    total_weight = (
        db.query(func.coalesce(func.sum(CollectionRequest.estimated_weight), 0.0))
        .filter(CollectionRequest.institution_id == current.id)
        .scalar()
    )

    return InstitutionDashboard(
        institution=InstitutionResponse.model_validate(current),
        total_collections=total_collections,
        total_weight_submitted=float(total_weight),
    )
