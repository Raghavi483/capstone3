"""
Health Check Endpoint (NFR-07)
Provides fast, lightweight liveness verification (<1s).
"""

from datetime import datetime, timezone
from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health", status_code=200)
def get_health():
    """Returns platform health status with ISO-8601 timestamp."""
    return {
        "status": "UP",
        "service": "medicard-settlement-platform",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
