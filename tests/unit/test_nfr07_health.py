"""
Test Suite: NFR-07 Health Check Endpoint
Requirements:
- GET /health returns HTTP 200
- Response arrives within 1.0 second
- Output payload contains status "UP"
"""

import time
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_nfr07_health_endpoint_status_and_latency():
    """NFR-07: Verifies HTTP 200 and <1s latency for /health."""
    start_time = time.perf_counter()
    response = client.get("/health")
    elapsed_time = time.perf_counter() - start_time

    assert response.status_code == 200
    assert elapsed_time < 1.0, f"Health check took {elapsed_time:.3f}s, exceeding 1s limit"
    
    data = response.json()
    assert data["status"] == "UP"
    assert "timestamp" in data
    assert data["service"] == "medicard-settlement-platform"
