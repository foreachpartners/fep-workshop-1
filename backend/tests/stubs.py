"""Test stubs and mocks."""

from unittest.mock import patch, MagicMock
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Callable

from feptm.models import Project, Specialist
from feptm.api.v1.periods import PaymentPeriod
from feptm.api.v1.timesheets import TimeEntry


@contextmanager
def mock_api_endpoint(endpoint_path: str, return_value: Any):
    """Mock FastAPI endpoint function to return a specific value.
    
    Args:
        endpoint_path: Path to the API endpoint function (e.g., "feptm.api.v1.specialists.get_specialists")
        return_value: Value to be returned by the mocked function
        
    Yields:
        MagicMock: The mock object
    """
    with patch(endpoint_path) as mock_func:
        mock_func.return_value = return_value
        yield mock_func


def create_mock_specialists() -> List[Specialist]:
    """Create mock specialists for testing.
    
    Returns:
        List of mock specialists
    """
    from feptm.models.specialist import SpecialistRole
    
    return [
        Specialist(
            id="s1",
            full_name="John Doe",
            email="john.doe@example.com",
            role=SpecialistRole.DEVELOPER.value,
            hourly_rate=50.0,
            start_date="2023-01-15T00:00:00Z"
        ),
        Specialist(
            id="s2",
            full_name="Jane Smith",
            email="jane.smith@example.com",
            role=SpecialistRole.PROJECT_MANAGER.value,
            hourly_rate=60.0,
            start_date="2022-09-01T00:00:00Z"
        )
    ]


def create_mock_projects() -> List[Project]:
    """Create mock projects for testing.
    
    Returns:
        List of mock projects
    """
    return [
        Project(
            id="p1",
            name="E-Commerce Platform"
        ),
        Project(
            id="p2",
            name="Mobile App"
        )
    ]


def create_mock_periods() -> List[PaymentPeriod]:
    """Create mock payment periods for testing.
    
    Returns:
        List of mock payment periods
    """
    return [
        PaymentPeriod(
            id="period1",
            name="January 2023",
            start_date="2023-01-01T00:00:00Z",
            end_date="2023-01-31T23:59:59Z",
            status="Closed"
        ),
        PaymentPeriod(
            id="period2",
            name="February 2023",
            start_date="2023-02-01T00:00:00Z",
            end_date="2023-02-28T23:59:59Z",
            status="Open"
        )
    ]


def create_mock_time_entries() -> List[TimeEntry]:
    """Create mock time entries for testing.
    
    Returns:
        List of mock time entries
    """
    return [
        TimeEntry(
            id="te1",
            date="2023-01-15T00:00:00Z",
            specialist_id="s1",
            project_id="p1",
            hours=8.0,
            description="Backend development"
        ),
        TimeEntry(
            id="te2",
            date="2023-01-16T00:00:00Z",
            specialist_id="s2",
            project_id="p1",
            hours=6.0,
            description="Project planning"
        )
    ] 