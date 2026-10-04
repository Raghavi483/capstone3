"""
Database connection and session management using SQLAlchemy and SQLite.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./medicard.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


DB_PATH = DATABASE_URL.replace("sqlite:///", "") if DATABASE_URL.startswith("sqlite") else DATABASE_URL


def get_db():
    """FastAPI dependency for database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_migrations():
    """Applies forward-only Alembic database migrations up to head (Priority 3)."""
    from pathlib import Path
    from alembic.config import Config
    from alembic import command

    project_root = Path(__file__).resolve().parent.parent.parent
    alembic_ini_path = project_root / "alembic.ini"
    alembic_cfg = Config(str(alembic_ini_path))
    alembic_cfg.set_main_option("script_location", str(project_root / "migrations"))
    alembic_cfg.set_main_option("sqlalchemy.url", DATABASE_URL)
    command.upgrade(alembic_cfg, "head")


def init_db():
    """Initializes tables in database using forward-only schema."""
    Base.metadata.create_all(bind=engine)
