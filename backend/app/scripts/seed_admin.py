"""
RePen India Backend — Admin Seed Script

Creates the initial admin account in the database.
Run once during initial setup:

    python -m app.scripts.seed_admin

Reads admin credentials from environment variables:
    ADMIN_EMAIL and ADMIN_PASSWORD

Falls back to prompting if not set.
"""

import os
import sys

# Ensure the backend dir is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.admin import Admin


def seed_admin():
    """Create the initial admin user."""
    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")

    if not email:
        email = input("Admin email: ").strip()
    if not password:
        password = input("Admin password: ").strip()

    if not email or not password:
        print("Error: email and password are required.")
        sys.exit(1)

    db = SessionLocal()
    try:
        # Check if admin already exists
        existing = db.query(Admin).filter(Admin.email == email).first()
        if existing:
            print(f"Admin '{email}' already exists. Skipping.")
            return

        admin = Admin(
            email=email,
            hashed_password=hash_password(password),
        )
        db.add(admin)
        db.commit()
        print(f"Admin '{email}' created successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_admin()
