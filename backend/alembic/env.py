"""
RePen India Backend — Alembic env.py

Configures Alembic to use the same database URL and ORM models
as the rest of the application, enabling auto-generated migrations.
"""

from logging.config import fileConfig

from sqlalchemy import create_engine, engine_from_config, pool
from alembic import context

# Import the app's Base and all models so Alembic discovers them
from app.core.database import Base
from app.core.config import get_settings
from app.models.institution import Institution  # noqa: F401
from app.models.collection_request import CollectionRequest  # noqa: F401
from app.models.admin import Admin  # noqa: F401

# Alembic config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the SQLAlchemy URL from our app settings
# NOTE: ConfigParser treats '%' as interpolation syntax, so we must
# escape it to '%%' before storing via set_main_option.
settings = get_settings()
config.set_main_option(
    "sqlalchemy.url",
    settings.database_url.replace("%", "%%"),
)

# Target metadata for autogenerate support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (generates SQL without connecting)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (connects to the database)."""
    # Create engine directly from settings URL to avoid ConfigParser
    # interpolation issues with special characters (e.g. %40 in passwords).
    connectable = create_engine(settings.database_url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
