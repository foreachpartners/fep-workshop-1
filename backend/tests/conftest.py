"""Common test fixtures and configuration."""

import pytest
from fastapi.testclient import TestClient

from feptm.main import app


@pytest.fixture
def client():
    """Create a test client for FastAPI application.
    
    Returns:
        TestClient: A FastAPI test client.
    """
    return TestClient(app)
