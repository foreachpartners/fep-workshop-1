"""Tests for the payment periods API endpoints."""

import pytest
from unittest.mock import patch, MagicMock
from fastapi import status

from feptm.api.v1.periods import PaymentPeriod
from tests.stubs import create_mock_periods, mock_api_endpoint


def test_get_payment_periods(client):
    """Test GET /api/periods endpoint."""
    # Get mock periods
    mock_periods = create_mock_periods()
    
    # Mock the API endpoint function
    with mock_api_endpoint("feptm.api.v1.periods.get_payment_periods", mock_periods):
        # Make the request
        response = client.get("/api/periods/")
        
        # Check that the response status code is 200 OK
        assert response.status_code == status.HTTP_200_OK
        
        # Check that the response data matches the mock data
        data = response.json()
        assert len(data) == 2
        assert data[0]["id"] == "period1"
        assert data[0]["name"] == "January 2023"
        assert data[1]["id"] == "period2"
        assert data[1]["name"] == "February 2023"


def test_get_payment_periods_with_filters(client):
    """Test GET /api/periods with filtering."""
    # Create filtered mock periods
    mock_period = create_mock_periods()[1]  # Second one has "Open" status
    
    # Define a custom filter_periods function for testing
    def filter_periods(status=None):
        if status == "Open":
            return [mock_period]
        return []
    
    # Mock the API endpoint with filter handling
    with patch("feptm.api.v1.periods.get_payment_periods") as mock_get:
        mock_get.side_effect = filter_periods
        
        # Make the request with query parameters
        response = client.get("/api/periods/?status=Open")
        
        # Check that the response status code is 200 OK
        assert response.status_code == status.HTTP_200_OK
        
        # Check that the response data matches the mock data
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == "period2"
        assert data[0]["name"] == "February 2023"
        assert data[0]["status"] == "Open"


def test_get_payment_period_by_id(client):
    """Test GET /api/periods/{period_id} endpoint."""
    # Get mock period
    mock_period = create_mock_periods()[0]
    
    # Mock the API endpoint function
    with mock_api_endpoint("feptm.api.v1.periods.get_payment_period", mock_period):
        # Make the request
        response = client.get("/api/periods/period1")
        
        # Check that the response status code is 200 OK
        assert response.status_code == status.HTTP_200_OK
        
        # Check that the response data matches the mock data
        data = response.json()
        assert data["id"] == "period1"
        assert data["name"] == "January 2023"
        assert data["status"] == "Closed"


def test_get_payment_period_not_found(client):
    """Test GET /api/periods/{period_id} with non-existent ID."""
    # Mock the API endpoint to return a 404 exception
    with patch("feptm.api.v1.periods.get_payment_period") as mock_get:
        # Set up the mock to raise HTTPException with 404 status
        mock_get.side_effect = lambda period_id: pytest.raises(
            status.HTTP_404_NOT_FOUND, 
            match=f"Payment period with ID {period_id} not found"
        )
        
        # Make the request
        response = client.get("/api/periods/non-existent")
        
        # Check that the response status code is 404 Not Found
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Check the error message
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()


def test_create_payment_period(client):
    """Test POST /api/periods/ endpoint."""
    # Mock period to return
    mock_period = PaymentPeriod(
        id="new-period",
        name="March 2023",
        start_date="2023-03-01T00:00:00Z",
        end_date="2023-03-31T23:59:59Z",
        status="Open"
    )
    
    # Request data
    request_data = {
        "name": "March 2023",
        "start_date": "2023-03-01T00:00:00Z",
        "end_date": "2023-03-31T23:59:59Z",
        "project_id": "p1"
    }
    
    # Mock the create_payment_period function
    with patch("feptm.api.v1.periods.create_payment_period") as mock_create:
        mock_create.return_value = mock_period
        
        # Make the request
        response = client.post("/api/periods/", json=request_data)
        
        # Check that the response status code is 200 OK
        assert response.status_code == status.HTTP_200_OK
        
        # Check the response data
        data = response.json()
        assert data["id"] == "new-period"
        assert data["name"] == "March 2023"
        assert data["start_date"] == "2023-03-01T00:00:00Z"
        assert data["end_date"] == "2023-03-31T23:59:59Z"
        assert data["status"] == "Open" 