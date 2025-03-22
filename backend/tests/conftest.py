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


@pytest.fixture
def mock_specialists_data():
    """Generate mock specialist data for tests.
    
    Returns:
        list: List of specialist dictionaries.
    """
    return [
        {
            "id": "s1",
            "full_name": "John Doe",
            "email": "john.doe@example.com",
            "role": "Developer",
            "hourly_rate": 50.0,
            "active": True,
            "hire_date": "2023-01-15T00:00:00Z",
            "leave_date": None
        },
        {
            "id": "s2",
            "full_name": "Jane Smith",
            "email": "jane.smith@example.com",
            "role": "Project Manager",
            "hourly_rate": 60.0,
            "active": True,
            "hire_date": "2022-09-01T00:00:00Z",
            "leave_date": None
        }
    ]


@pytest.fixture
def mock_projects_data():
    """Generate mock project data for tests.
    
    Returns:
        list: List of project dictionaries.
    """
    return [
        {
            "id": "p1",
            "name": "Project Alpha",
            "client": "Client A",
            "start_date": "2023-02-01T00:00:00Z",
            "end_date": None,
            "budget": 100000.0,
            "status": "Active"
        },
        {
            "id": "p2",
            "name": "Project Beta",
            "client": "Client B",
            "start_date": "2023-01-15T00:00:00Z",
            "end_date": "2023-06-15T00:00:00Z",
            "budget": 50000.0,
            "status": "Completed"
        }
    ]


@pytest.fixture
def mock_time_entries():
    """Generate mock time entry data for tests.
    
    Returns:
        list: List of time entry dictionaries.
    """
    return [
        {
            "id": "t1",
            "specialist_id": "s1",
            "project_id": "p1",
            "date": "2023-03-01",
            "hours": 8.0,
            "description": "Development work"
        },
        {
            "id": "t2",
            "specialist_id": "s2",
            "project_id": "p1",
            "date": "2023-03-01",
            "hours": 6.0,
            "description": "Project management"
        }
    ]


@pytest.fixture
def mock_payment_periods():
    """Generate mock payment period data for tests.
    
    Returns:
        list: List of payment period dictionaries.
    """
    return [
        {
            "id": "pp1",
            "name": "March 2023",
            "start_date": "2023-03-01",
            "end_date": "2023-03-31",
            "status": "Open"
        },
        {
            "id": "pp2",
            "name": "February 2023",
            "start_date": "2023-02-01",
            "end_date": "2023-02-28",
            "status": "Closed"
        }
    ] 