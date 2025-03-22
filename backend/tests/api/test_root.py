"""Tests for the root API endpoint."""

from fastapi import status


def test_root_endpoint(client):
    """Test GET / endpoint."""
    response = client.get("/")
    
    # Check that the response status code is 200 OK
    assert response.status_code == status.HTTP_200_OK
    
    # Check that the response data contains expected fields
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"
    assert "message" in data
    assert "Time & Materials accounting service is running" in data["message"] 