"""Tests for the payment periods API endpoints."""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, date
from fastapi import status

from feptm.models import PaymentPeriod
from feptm.models.payment import TimeEntry, PeriodStatus


def test_get_payment_periods(client):
    """Test GET /api/periods endpoint."""
    # Test data - определено прямо в тесте для лучшей читаемости
    mock_periods = [
        PaymentPeriod(
            id="pp1",
            name="March 2023",
            start_date=date(2023, 3, 1),
            end_date=date(2023, 3, 31),
            status=PeriodStatus.OPEN,
            time_entries=[]
        ),
        PaymentPeriod(
            id="pp2",
            name="February 2023",
            start_date=date(2023, 2, 1),
            end_date=date(2023, 2, 28),
            status=PeriodStatus.CLOSED,
            time_entries=[]
        )
    ]
    
    # Mock the get_filtered_data method
    with patch('feptm.services.mock_data_service.mock_data_service.get_filtered_data') as mock_get_filtered:
        # Set up the mock to return the test data
        mock_get_filtered.return_value = mock_periods
        
        # Make the request
        response = client.get("/api/periods/")
        
        # Check that the response status code is 200 OK
        assert response.status_code == status.HTTP_200_OK
        
        # Check that the mock was called with the correct arguments
        mock_get_filtered.assert_called_once_with("payment_periods", {})
        
        # Check that the response data matches the mock data
        data = response.json()
        assert len(data) == 2
        assert data[0]["id"] == "pp1"
        assert data[0]["name"] == "March 2023"
        assert data[0]["status"] == "Open"
        assert data[1]["id"] == "pp2"
        assert data[1]["name"] == "February 2023"
        assert data[1]["status"] == "Closed"


def test_get_payment_periods_with_status_filter(client):
    """Test GET /api/periods with status filter."""
    # Test data - определено прямо в тесте для лучшей читаемости
    mock_periods = [
        PaymentPeriod(
            id="pp1",
            name="March 2023",
            start_date=date(2023, 3, 1),
            end_date=date(2023, 3, 31),
            status=PeriodStatus.OPEN,
            time_entries=[]
        )
    ]
    
    # Mock the get_filtered_data method
    with patch('feptm.services.mock_data_service.mock_data_service.get_filtered_data') as mock_get_filtered:
        # Set up the mock to return the test data
        mock_get_filtered.return_value = mock_periods
        
        # Make the request with query parameters
        response = client.get("/api/periods/?status=Open")
        
        # Check that the response status code is 200 OK
        assert response.status_code == status.HTTP_200_OK
        
        # Check that the mock was called with the correct arguments
        mock_get_filtered.assert_called_once_with("payment_periods", {"status": "Open"})
        
        # Check that the response data matches the mock data
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == "pp1"
        assert data[0]["name"] == "March 2023"
        assert data[0]["status"] == "Open"


def test_get_payment_period_by_id(client):
    """Test GET /api/periods/{period_id} endpoint."""
    # Test data - определено прямо в тесте для лучшей читаемости
    mock_period = PaymentPeriod(
        id="pp1",
        name="March 2023",
        start_date=date(2023, 3, 1),
        end_date=date(2023, 3, 31),
        status=PeriodStatus.OPEN,
        time_entries=[]
    )
    
    # Mock the get_payment_period method
    with patch('feptm.services.mock_data_service.mock_data_service.get_payment_period') as mock_get_period:
        # Set up the mock to return the test data
        mock_get_period.return_value = mock_period
        
        # Make the request
        response = client.get("/api/periods/pp1")
        
        # Check that the response status code is 200 OK
        assert response.status_code == status.HTTP_200_OK
        
        # Check that the mock was called with the correct arguments
        mock_get_period.assert_called_once_with("pp1")
        
        # Check that the response data matches the mock data
        data = response.json()
        assert data["id"] == "pp1"
        assert data["name"] == "March 2023"
        assert data["start_date"].startswith("2023-03-01")
        assert data["end_date"].startswith("2023-03-31")
        assert data["status"] == "Open"


def test_get_payment_period_not_found(client):
    """Test GET /api/periods/{period_id} with non-existent ID."""
    # Mock the get_payment_period method
    with patch('feptm.services.mock_data_service.mock_data_service.get_payment_period') as mock_get_period:
        # Set up the mock to return None (payment period not found)
        mock_get_period.return_value = None
        
        # Make the request
        response = client.get("/api/periods/non-existent")
        
        # Check that the response status code is 404 Not Found
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Check that the mock was called with the correct arguments
        mock_get_period.assert_called_once_with("non-existent")
        
        # Check the error message
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()


def test_get_period_time_entries(client):
    """Test GET /api/periods/{period_id}/time-entries endpoint."""
    # Test data - определено прямо в тесте для лучшей читаемости
    mock_entries = [
        TimeEntry(
            id="t1",
            specialist_id="s1",
            project_id="p1",
            date=date(2023, 3, 1),
            hours=8.0,
            description="Development work"
        ),
        TimeEntry(
            id="t2",
            specialist_id="s2",
            project_id="p1",
            date=date(2023, 3, 1),
            hours=6.0,
            description="Project management"
        )
    ]
    
    mock_period = PaymentPeriod(
        id="pp1",
        name="March 2023",
        start_date=date(2023, 3, 1),
        end_date=date(2023, 3, 31),
        status=PeriodStatus.OPEN,
        time_entries=mock_entries
    )
    
    # Mock the get_payment_period method
    with patch('feptm.services.mock_data_service.mock_data_service.get_payment_period') as mock_get_period:
        # Set up the mock to return the test data
        mock_get_period.return_value = mock_period
        
        # Make the request
        response = client.get("/api/periods/pp1/time-entries")
        
        # Check that the response status code is 200 OK
        assert response.status_code == status.HTTP_200_OK
        
        # Check that the mock was called with the correct arguments
        mock_get_period.assert_called_once_with("pp1")
        
        # Check that the response data matches the mock data
        data = response.json()
        assert len(data) == 2
        assert data[0]["id"] == "t1"
        assert data[0]["specialist_id"] == "s1"
        assert data[0]["project_id"] == "p1"
        assert data[0]["hours"] == 8.0
        assert data[1]["id"] == "t2"
        assert data[1]["specialist_id"] == "s2"
        assert data[1]["hours"] == 6.0


def test_get_period_time_entries_with_filters(client):
    """Test GET /api/periods/{period_id}/time-entries with filters."""
    # Test data - определено прямо в тесте для лучшей читаемости
    mock_entries = [
        TimeEntry(
            id="t1",
            specialist_id="s1",
            project_id="p1",
            date=date(2023, 3, 1),
            hours=8.0,
            description="Development work"
        ),
        TimeEntry(
            id="t2",
            specialist_id="s2",
            project_id="p1",
            date=date(2023, 3, 1),
            hours=6.0,
            description="Project management"
        ),
        TimeEntry(
            id="t3",
            specialist_id="s1",
            project_id="p2",
            date=date(2023, 3, 2),
            hours=4.0,
            description="Design review"
        )
    ]
    
    mock_period = PaymentPeriod(
        id="pp1",
        name="March 2023",
        start_date=date(2023, 3, 1),
        end_date=date(2023, 3, 31),
        status=PeriodStatus.OPEN,
        time_entries=mock_entries
    )
    
    # Mock the get_payment_period method
    with patch('feptm.services.mock_data_service.mock_data_service.get_payment_period') as mock_get_period:
        # Set up the mock to return the test data
        mock_get_period.return_value = mock_period
        
        # Make the request with specialist_id filter
        response = client.get("/api/periods/pp1/time-entries?specialist_id=s1")
        
        # Check that the response status code is 200 OK
        assert response.status_code == status.HTTP_200_OK
        
        # Check that the mock was called with the correct arguments
        mock_get_period.assert_called_once_with("pp1")
        
        # Check that the response data matches the filtered mock data
        data = response.json()
        assert len(data) == 2
        assert all(entry["specialist_id"] == "s1" for entry in data)
        
        # Reset the mock for the next request
        mock_get_period.reset_mock()
        mock_get_period.return_value = mock_period
        
        # Make the request with project_id filter
        response = client.get("/api/periods/pp1/time-entries?project_id=p1")
        
        # Check that the response status code is 200 OK
        assert response.status_code == status.HTTP_200_OK
        
        # Check that the response data matches the filtered mock data
        data = response.json()
        assert len(data) == 2
        assert all(entry["project_id"] == "p1" for entry in data)
        
        # Reset the mock for the next request
        mock_get_period.reset_mock()
        mock_get_period.return_value = mock_period
        
        # Make the request with both filters
        response = client.get("/api/periods/pp1/time-entries?specialist_id=s1&project_id=p1")
        
        # Check that the response status code is 200 OK
        assert response.status_code == status.HTTP_200_OK
        
        # Check that the response data matches the filtered mock data
        data = response.json()
        assert len(data) == 1
        assert data[0]["specialist_id"] == "s1"
        assert data[0]["project_id"] == "p1"


def test_get_period_time_entries_period_not_found(client):
    """Test GET /api/periods/{period_id}/time-entries with non-existent period ID."""
    # Mock the get_payment_period method
    with patch('feptm.services.mock_data_service.mock_data_service.get_payment_period') as mock_get_period:
        # Set up the mock to return None (payment period not found)
        mock_get_period.return_value = None
        
        # Make the request
        response = client.get("/api/periods/non-existent/time-entries")
        
        # Check that the response status code is 404 Not Found
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Check the error message
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower() 