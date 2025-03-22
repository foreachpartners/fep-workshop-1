"""Tests for the specialists API endpoints."""

import pytest
from unittest.mock import patch, MagicMock
from fastapi import status

from feptm.models import Specialist
from feptm.models.specialist import SpecialistRole


def test_get_specialists(client):
    """Test GET /api/specialists endpoint."""
    # Test data - определено прямо в тесте для лучшей читаемости
    mock_specialists = [
        Specialist(
            id="s1",
            full_name="John Doe",
            email="john.doe@example.com",
            role=SpecialistRole.DEVELOPER,
            hourly_rate=50.0,
            active=True,
            hire_date="2023-01-15T00:00:00Z"
        ),
        Specialist(
            id="s2",
            full_name="Jane Smith",
            email="jane.smith@example.com",
            role=SpecialistRole.PROJECT_MANAGER,
            hourly_rate=60.0,
            active=True,
            hire_date="2022-09-01T00:00:00Z"
        )
    ]
    
    # Mock the get_filtered_data method
    with patch('feptm.services.mock_data_service.mock_data_service.get_filtered_data') as mock_get_filtered:
        # Set up the mock to return the test data
        mock_get_filtered.return_value = mock_specialists
        
        # Make the request
        response = client.get("/api/specialists/")
        
        # Check that the response status code is 200 OK
        assert response.status_code == status.HTTP_200_OK
        
        # Check that the mock was called with the correct arguments
        mock_get_filtered.assert_called_once_with("specialists", {})
        
        # Check that the response data matches the mock data
        data = response.json()
        assert len(data) == 2
        assert data[0]["id"] == "s1"
        assert data[0]["full_name"] == "John Doe"
        assert data[1]["id"] == "s2"
        assert data[1]["full_name"] == "Jane Smith"


def test_get_specialists_with_filters(client):
    """Test GET /api/specialists with filtering."""
    # Test data - определено прямо в тесте для лучшей читаемости
    mock_specialists = [
        Specialist(
            id="s1",
            full_name="John Doe",
            email="john.doe@example.com",
            role=SpecialistRole.DEVELOPER,
            hourly_rate=50.0,
            active=True,
            hire_date="2023-01-15T00:00:00Z"
        )
    ]
    
    # Mock the get_filtered_data method
    with patch('feptm.services.mock_data_service.mock_data_service.get_filtered_data') as mock_get_filtered:
        # Set up the mock to return the test data
        mock_get_filtered.return_value = mock_specialists
        
        # Make the request with query parameters
        response = client.get("/api/specialists/?active=true&role=Developer")
        
        # Check that the response status code is 200 OK
        assert response.status_code == status.HTTP_200_OK
        
        # Check that the mock was called with the correct arguments
        mock_get_filtered.assert_called_once_with("specialists", {"active": True, "role": "Developer"})
        
        # Check that the response data matches the mock data
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == "s1"
        assert data[0]["full_name"] == "John Doe"
        assert data[0]["role"] == "Developer"
        assert data[0]["active"] is True


def test_get_specialist_by_id(client):
    """Test GET /api/specialists/{specialist_id} endpoint."""
    # Test data - определено прямо в тесте для лучшей читаемости
    mock_specialist = Specialist(
        id="s1",
        full_name="John Doe",
        email="john.doe@example.com",
        role=SpecialistRole.DEVELOPER,
        hourly_rate=50.0,
        active=True,
        hire_date="2023-01-15T00:00:00Z"
    )
    
    # Mock the get_specialist method
    with patch('feptm.services.mock_data_service.mock_data_service.get_specialist') as mock_get_specialist:
        # Set up the mock to return the test data
        mock_get_specialist.return_value = mock_specialist
        
        # Make the request
        response = client.get("/api/specialists/s1")
        
        # Check that the response status code is 200 OK
        assert response.status_code == status.HTTP_200_OK
        
        # Check that the mock was called with the correct arguments
        mock_get_specialist.assert_called_once_with("s1")
        
        # Check that the response data matches the mock data
        data = response.json()
        assert data["id"] == "s1"
        assert data["full_name"] == "John Doe"
        assert data["email"] == "john.doe@example.com"
        assert data["role"] == "Developer"
        assert data["hourly_rate"] == 50.0
        assert data["active"] is True


def test_get_specialist_not_found(client):
    """Test GET /api/specialists/{specialist_id} with non-existent ID."""
    # Mock the get_specialist method
    with patch('feptm.services.mock_data_service.mock_data_service.get_specialist') as mock_get_specialist:
        # Set up the mock to return None (specialist not found)
        mock_get_specialist.return_value = None
        
        # Make the request
        response = client.get("/api/specialists/non-existent")
        
        # Check that the response status code is 404 Not Found
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Check that the mock was called with the correct arguments
        mock_get_specialist.assert_called_once_with("non-existent")
        
        # Check the error message
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower() 