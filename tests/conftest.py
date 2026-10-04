"""
Pytest configuration and session fixtures for MediCard.
Ensures deterministic synthetic test data is seeded fresh.
"""

import pytest
from src.seed_data import seed_database


@pytest.fixture(scope="session", autouse=True)
def setup_test_suite_db():
    """Initializes and seeds fresh test database for test session."""
    seed_database(force=True)
    yield
