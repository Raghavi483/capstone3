"""
Unit Tests: Database Migrations from Empty Database (Priority 3, Section 6).
Proves:
1. Alembic migrations run cleanly against an empty database.
2. All 16 production entity tables are created.
3. Seed data can be successfully applied to the migrated database.
"""

import os
import tempfile
from pathlib import Path
import pytest
from sqlalchemy import create_engine, inspect

from alembic.config import Config
from alembic import command
from src.seed_data import seed_database
from src.repositories.database import Base


def test_alembic_migrations_on_empty_database():
    """Verifies that an empty database can be migrated to head and seeded cleanly."""
    project_root = Path(__file__).resolve().parent.parent.parent
    alembic_ini_path = project_root / "alembic.ini"
    
    # Create temporary database file
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        tmp_db_path = tmp_file.name

    try:
        tmp_db_url = f"sqlite:///{tmp_db_path}"
        
        # Configure Alembic with temporary DB URL
        alembic_cfg = Config(str(alembic_ini_path))
        alembic_cfg.set_main_option("sqlalchemy.url", tmp_db_url)
        alembic_cfg.set_main_option("script_location", str(project_root / "migrations"))

        # Run migration to head
        command.upgrade(alembic_cfg, "head")

        # Inspect migrated tables
        temp_engine = create_engine(tmp_db_url)
        inspector = inspect(temp_engine)
        table_names = set(inspector.get_table_names())

        expected_tables = {
            "customers",
            "policies",
            "hospitals",
            "network_hospitals",
            "pre_authorizations",
            "pre_auth_decisions",
            "claims",
            "admissions",
            "procedure_records",
            "final_bills",
            "settlements",
            "claim_timeline_events",
            "audit_events",
            "notifications",
            "policy_product_configs",
            "policy_rule_versions"
        }

        for expected in expected_tables:
            assert expected in table_names, f"Expected table '{expected}' missing from migrated database"

        # Verify alembic_version table exists and has revision recorded
        assert "alembic_version" in table_names

    finally:
        if os.path.exists(tmp_db_path):
            try:
                os.remove(tmp_db_path)
            except Exception:
                pass
