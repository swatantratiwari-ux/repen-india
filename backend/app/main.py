"""
RePen India Backend — Main Application Entry Point

Assembles the FastAPI app, configures CORS, and mounts all routers.
Disables interactive docs in production.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.routes import institutions, collections, admin

settings = get_settings()

# --- App Factory ---
# Disable Swagger/ReDoc in production to reduce attack surface
app = FastAPI(
    title="RePen India API",
    description=(
        "Backend API for the RePen India pen recycling platform. "
        "Manages institution registration, collection requests, "
        "and admin operations."
    ),
    version="1.0.0",
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None if settings.is_production else "/redoc",
)

# --- CORS Middleware ---
# Restrict methods to only those actually used by the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# --- Mount Routers ---
API_V1 = "/api/v1"

app.include_router(institutions.router, prefix=API_V1)
app.include_router(collections.router, prefix=API_V1)
app.include_router(admin.router, prefix=API_V1)


# --- Health Check ---
@app.get("/health", tags=["Health"])
def health_check():
    """Simple health check endpoint for monitoring."""
    return {"status": "healthy", "service": "repen-india-api"}
