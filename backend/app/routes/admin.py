"""
RePen India Backend — Admin Routes

Endpoints:
    POST /login         — Admin login (JWT)
    GET  /institutions  — List all registered institutions (protected)
    PATCH /collections/{id}/status — Update collection request status (protected)
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    verify_password,
    create_access_token,
    get_current_admin,
)
from app.models.admin import Admin
from app.models.institution import Institution
from app.models.collection_request import CollectionRequest, CollectionStatus
from app.schemas.admin import AdminLogin, AdminResponse
from app.schemas.institution import InstitutionResponse
from app.schemas.collection_request import (
    CollectionStatusUpdate,
    CollectionRequestResponse,
)
from app.schemas.token import TokenResponse

router = APIRouter(prefix="/admin", tags=["Admin"])


# --- Admin Login ---
@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Admin login",
)
def admin_login(
    data: AdminLogin,
    db: Session = Depends(get_db),
):
    """
    Verify admin credentials and return a JWT access token
    with role='admin'.
    """
    admin = db.query(Admin).filter(Admin.email == data.email).first()

    if not admin or not verify_password(data.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    token = create_access_token(subject=admin.email, role="admin")
    return TokenResponse(access_token=token)


# --- List All Institutions ---
@router.get(
    "/institutions",
    response_model=list[InstitutionResponse],
    summary="List all registered institutions",
)
def list_all_institutions(
    _: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Return all registered institutions. Admin-only."""
    return (
        db.query(Institution)
        .order_by(Institution.created_at.desc())
        .all()
    )


# --- Update Collection Status ---
@router.patch(
    "/collections/{collection_id}/status",
    response_model=CollectionRequestResponse,
    summary="Update a collection request status",
)
def update_collection_status(
    collection_id: UUID,
    data: CollectionStatusUpdate,
    _: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Update the status of any collection request.
    Admin-only endpoint.
    Enforces valid transitions: pending → approved → completed.
    """
    collection = db.query(CollectionRequest).filter(
        CollectionRequest.id == collection_id
    ).first()

    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection request not found",
        )

    # Enforce valid status transitions
    valid_transitions = {
        CollectionStatus.PENDING: {CollectionStatus.APPROVED},
        CollectionStatus.APPROVED: {CollectionStatus.COMPLETED},
        CollectionStatus.COMPLETED: set(),  # terminal state
    }

    allowed = valid_transitions.get(collection.status, set())
    if data.status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Cannot transition from '{collection.status.value}' to '{data.status.value}'. "
                   f"Allowed: {', '.join(s.value for s in allowed) or 'none (terminal state)'}",
        )

    collection.status = data.status
    db.commit()
    db.refresh(collection)

    return collection
