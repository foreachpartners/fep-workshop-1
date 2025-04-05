"""Tests for the root API endpoint."""

import pytest
from fastapi import status


def test_root_endpoint(client):
    """Test that the root endpoint returns a welcome message."""
    response = client.get("/api/")
    
    assert response.status_code == status.HTTP_200_OK
    assert "message" in response.json()
    assert "welcome" in response.json()["message"].lower() 