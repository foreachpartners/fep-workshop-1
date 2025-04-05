"""Tests for the specialists API endpoints."""

import pytest
from unittest.mock import patch, MagicMock
from fastapi import status

from feptm.models import Specialist
from tests.stubs import create_mock_specialists, mock_api_endpoint


def test_get_specialists(client):
    """Test GET /api/specialists endpoint."""
    # Get mock specialists
    mock_specialists = create_mock_specialists()
    
    # Mock the API endpoint function
    with mock_api_endpoint("feptm.api.v1.specialists.get_specialists", mock_specialists):
        # Make the request
        response = client.get("/api/specialists/")
        
        # Check that the response status code is 200 OK
        assert response.status_code == status.HTTP_200_OK
        
        # Check that the response data matches the mock data
        data = response.json()
        assert len(data) == 2
        assert data[0]["id"] == "s1"
        assert data[0]["full_name"] == "John Doe"
        assert data[1]["id"] == "s2"
        assert data[1]["full_name"] == "Jane Smith"


def test_get_specialists_with_filters(client):
    """Test GET /api/specialists with filtering."""
    # Create filtered mock specialists
    mock_specialist = create_mock_specialists()[0]  # Just use the first one
    
    # Define a custom filter_specialists function for testing
    def filter_specialists(active=None, role=None):
        if active is True and role == "Developer":
            return [mock_specialist]
        return []
    
    # Mock the API endpoint with filter handling
    with patch("feptm.api.v1.specialists.get_specialists") as mock_get:
        mock_get.side_effect = filter_specialists
        
        # Make the request with query parameters
        response = client.get("/api/specialists/?active=true&role=Developer")
        
        # Check that the response status code is 200 OK
        assert response.status_code == status.HTTP_200_OK
        
        # Check that the response data matches the mock data
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == "s1"
        assert data[0]["full_name"] == "John Doe"
        assert data[0]["role"] == "Developer"


def test_get_specialist_by_id(client):
    """Test GET /api/specialists/{specialist_id} endpoint."""
    # Get mock specialist
    mock_specialist = create_mock_specialists()[0]
    
    # Mock the API endpoint function
    with mock_api_endpoint("feptm.api.v1.specialists.get_specialist", mock_specialist):
        # Make the request
        response = client.get("/api/specialists/s1")
        
        # Check that the response status code is 200 OK
        assert response.status_code == status.HTTP_200_OK
        
        # Check that the response data matches the mock data
        data = response.json()
        assert data["id"] == "s1"
        assert data["full_name"] == "John Doe"
        assert data["email"] == "john.doe@example.com"
        assert data["role"] == "Developer"
        assert data["hourly_rate"] == 50.0


def test_get_specialist_not_found(client):
    """Test GET /api/specialists/{specialist_id} with non-existent ID."""
    # Mock the API endpoint to return a 404 exception
    with patch("feptm.api.v1.specialists.get_specialist") as mock_get:
        # Set up the mock to raise HTTPException with 404 status
        mock_get.side_effect = lambda specialist_id: pytest.raises(
            status.HTTP_404_NOT_FOUND, 
            match=f"Specialist with ID {specialist_id} not found"
        )
        
        # Make the request
        response = client.get("/api/specialists/non-existent")
        
        # Check that the response status code is 404 Not Found
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Check the error message
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower() 