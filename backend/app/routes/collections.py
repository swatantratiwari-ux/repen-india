"""
RePen India Backend — Collection Request Routes

Endpoints:
    POST /  — Create a new collection request (institution, protected)
    GET  /  — List collection requests for current institution (protected)
    GET  /{id} — Get a specific collection request (protected)
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_institution
from app.models.institution import Institution
from app.models.collection_request import CollectionRequest, CollectionStatus
from app.schemas.collection_request import (
    CollectionRequestCreate,
    CollectionRequestResponse,
)

router = APIRouter(prefix="/collections", tags=["Collections"])


# --- Create Collection Request ---
@router.post(
    "/",
    response_model=CollectionRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a collection pickup request",
)
def create_collection(
    data: CollectionRequestCreate,
    current: Institution = Depends(get_current_institution),
    db: Session = Depends(get_db),
):
    """
    Submit a new pen collection pickup request.
    Automatically linked to the authenticated institution.
    Initial status is always 'pending'.
    """
    collection = CollectionRequest(
        institution_id=current.id,
        estimated_weight=data.estimated_weight,
        pickup_address=data.pickup_address,
        status=CollectionStatus.PENDING,
    )
    db.add(collection)
    db.commit()
    db.refresh(collection)

    return collection


# --- List My Collections ---
@router.get(
    "/",
    response_model=list[CollectionRequestResponse],
    summary="List my collection requests",
)
def list_collections(
    current: Institution = Depends(get_current_institution),
    db: Session = Depends(get_db),
):
    """Return all collection requests for the authenticated institution."""
    collections = (
        db.query(CollectionRequest)
        .filter(CollectionRequest.institution_id == current.id)
        .order_by(CollectionRequest.created_at.desc())
        .all()
    )
    return collections


# --- Get Single Collection ---
@router.get(
    "/{collection_id}",
    response_model=CollectionRequestResponse,
    summary="Get a specific collection request",
)
def get_collection(
    collection_id: UUID,
    current: Institution = Depends(get_current_institution),
    db: Session = Depends(get_db),
):
    """
    Fetch a specific collection request by ID.
    Only accessible if it belongs to the authenticated institution.
    """
    collection = (
        db.query(CollectionRequest)
        .filter(
            CollectionRequest.id == collection_id,
            CollectionRequest.institution_id == current.id,
        )
        .first()
    )

    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection request not found",
        )

    return collection
