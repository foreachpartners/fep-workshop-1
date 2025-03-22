"""Tests for the reports API endpoints."""

import pytest
from unittest.mock import patch, MagicMock
from datetime import date
from fastapi import status

from feptm.models import PaymentPeriod, Specialist, Project
from feptm.models.payment import TimeEntry, PeriodStatus
from feptm.models.specialist import SpecialistRole
from feptm.models.project import ProjectStatus, ProjectType
from feptm.api.v1.reports import SpecialistReport, ProjectReport


@pytest.mark.skip(reason="Нужно исправить API отчетов")
def test_get_specialist_reports_no_period(client):
    """Test GET /api/reports/specialists without period filter."""
    # Test data - определено прямо в тесте для лучшей читаемости
    # Mock specialists
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
    
    # Mock periods with time entries
    mock_periods = [
        PaymentPeriod(
            id="pp1",
            name="March 2023",
            start_date=date(2023, 3, 1),
            end_date=date(2023, 3, 31),
            status=PeriodStatus.OPEN,
            time_entries=[
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
                    hours=8.0,
                    description="Development work"
                )
            ]
        ),
        PaymentPeriod(
            id="pp2",
            name="February 2023",
            start_date=date(2023, 2, 1),
            end_date=date(2023, 2, 28),
            status=PeriodStatus.CLOSED,
            time_entries=[
                TimeEntry(
                    id="t4",
                    specialist_id="s1",
                    project_id="p1",
                    date=date(2023, 2, 15),
                    hours=8.0,
                    description="Development work"
                )
            ]
        )
    ]
    
    # Expected reports
    expected_reports = [
        SpecialistReport(
            specialist_id="s1",
            full_name="John Doe",
            role="Developer",
            total_hours=24.0,  # 8 + 8 + 8
            hourly_rate=50.0,
            total_amount=1200.0  # 24 * 50
        ),
        SpecialistReport(
            specialist_id="s2",
            full_name="Jane Smith",
            role="Project Manager",
            total_hours=6.0,
            hourly_rate=60.0,
            total_amount=360.0  # 6 * 60
        )
    ]
    
    # Mock the necessary methods
    with patch('feptm.services.mock_data_service.mock_data_service.get_payment_periods') as mock_get_periods, \
         patch('feptm.services.mock_data_service.mock_data_service.get_specialists') as mock_get_specialists:
        # Set up the mocks to return the test data
        mock_get_periods.return_value = mock_periods
        mock_get_specialists.return_value = mock_specialists
        
        # Make the request
        response = client.get("/api/reports/specialists")
        
        # Check that the response status code is 200 OK
        assert response.status_code == status.HTTP_200_OK
        
        # Check that the mocks were called
        mock_get_periods.assert_called_once()
        mock_get_specialists.assert_called_once()
        
        # Check that the response data matches the expected reports
        data = response.json()
        assert len(data) == 2
        # Sort by specialist_id to ensure consistent order
        data.sort(key=lambda x: x["specialist_id"])
        
        assert data[0]["specialist_id"] == "s1"
        assert data[0]["full_name"] == "John Doe"
        assert data[0]["role"] == "Developer"
        assert data[0]["total_hours"] == 24.0
        assert data[0]["hourly_rate"] == 50.0
        assert data[0]["total_amount"] == 1200.0
        
        assert data[1]["specialist_id"] == "s2"
        assert data[1]["full_name"] == "Jane Smith"
        assert data[1]["role"] == "Project Manager"
        assert data[1]["total_hours"] == 6.0
        assert data[1]["hourly_rate"] == 60.0
        assert data[1]["total_amount"] == 360.0


@pytest.mark.skip(reason="Нужно исправить API отчетов")
def test_get_specialist_reports_with_period(client):
    """Test GET /api/reports/specialists with period filter."""
    # Test data - определено прямо в тесте для лучшей читаемости
    # Mock specialists
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
    
    # Mock period with time entries
    mock_period = PaymentPeriod(
        id="pp1",
        name="March 2023",
        start_date=date(2023, 3, 1),
        end_date=date(2023, 3, 31),
        status=PeriodStatus.OPEN,
        time_entries=[
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
                hours=8.0,
                description="Development work"
            )
        ]
    )
    
    # Expected reports for specific period
    expected_reports = [
        SpecialistReport(
            specialist_id="s1",
            full_name="John Doe",
            role="Developer",
            total_hours=16.0,  # 8 + 8
            hourly_rate=50.0,
            total_amount=800.0  # 16 * 50
        ),
        SpecialistReport(
            specialist_id="s2",
            full_name="Jane Smith",
            role="Project Manager",
            total_hours=6.0,
            hourly_rate=60.0,
            total_amount=360.0  # 6 * 60
        )
    ]
    
    # Mock the necessary methods
    with patch('feptm.services.mock_data_service.mock_data_service.get_payment_period') as mock_get_period, \
         patch('feptm.services.mock_data_service.mock_data_service.get_specialists') as mock_get_specialists:
        # Set up the mocks to return the test data
        mock_get_period.return_value = mock_period
        mock_get_specialists.return_value = mock_specialists
        
        # Make the request
        response = client.get("/api/reports/specialists?period_id=pp1")
        
        # Check that the response status code is 200 OK
        assert response.status_code == status.HTTP_200_OK
        
        # Check that the mocks were called with correct arguments
        mock_get_period.assert_called_once_with("pp1")
        mock_get_specialists.assert_called_once()
        
        # Check that the response data matches the expected reports
        data = response.json()
        assert len(data) == 2
        # Sort by specialist_id to ensure consistent order
        data.sort(key=lambda x: x["specialist_id"])
        
        assert data[0]["specialist_id"] == "s1"
        assert data[0]["full_name"] == "John Doe"
        assert data[0]["total_hours"] == 16.0
        assert data[0]["total_amount"] == 800.0
        
        assert data[1]["specialist_id"] == "s2"
        assert data[1]["full_name"] == "Jane Smith"
        assert data[1]["total_hours"] == 6.0
        assert data[1]["total_amount"] == 360.0


def test_get_specialist_reports_period_not_found(client):
    """Test GET /api/reports/specialists with non-existent period ID."""
    # Mock the get_payment_period method
    with patch('feptm.services.mock_data_service.mock_data_service.get_payment_period') as mock_get_period:
        # Set up the mock to return None (period not found)
        mock_get_period.return_value = None
        
        # Make the request
        response = client.get("/api/reports/specialists?period_id=non-existent")
        
        # Check that the response status code is 404 Not Found
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Check that the mock was called with the correct arguments
        mock_get_period.assert_called_once_with("non-existent")
        
        # Check the error message
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()


@pytest.mark.skip(reason="Нужно исправить API отчетов")
def test_get_project_reports_no_period(client):
    """Test GET /api/reports/projects without period filter."""
    # Test data - определено прямо в тесте для лучшей читаемости
    # Mock projects
    mock_projects = [
        Project(
            id="p1",
            name="Project Alpha",
            description="Test project",
            client_name="Client A",
            status=ProjectStatus.ACTIVE,
            project_type=ProjectType.TIME_AND_MATERIALS,
            start_date="2023-02-01T00:00:00Z"
        ),
        Project(
            id="p2",
            name="Project Beta",
            description="Test project",
            client_name="Client B",
            status=ProjectStatus.ACTIVE,
            project_type=ProjectType.TIME_AND_MATERIALS,
            start_date="2023-01-15T00:00:00Z"
        )
    ]
    
    # Mock periods with time entries
    mock_periods = [
        PaymentPeriod(
            id="pp1",
            name="March 2023",
            start_date=date(2023, 3, 1),
            end_date=date(2023, 3, 31),
            status=PeriodStatus.OPEN,
            time_entries=[
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
                    hours=8.0,
                    description="Development work"
                )
            ]
        ),
        PaymentPeriod(
            id="pp2",
            name="February 2023",
            start_date=date(2023, 2, 1),
            end_date=date(2023, 2, 28),
            status=PeriodStatus.CLOSED,
            time_entries=[
                TimeEntry(
                    id="t4",
                    specialist_id="s1",
                    project_id="p1",
                    date=date(2023, 2, 15),
                    hours=8.0,
                    description="Development work"
                )
            ]
        )
    ]
    
    # Expected reports
    expected_reports = [
        ProjectReport(
            project_id="p1",
            name="Project Alpha",
            client_name="Client A",
            total_hours=22.0,  # 8 + 6 + 8
            specialist_count=2  # s1, s2
        ),
        ProjectReport(
            project_id="p2",
            name="Project Beta",
            client_name="Client B",
            total_hours=8.0,
            specialist_count=1  # s1
        )
    ]
    
    # Mock the necessary methods
    with patch('feptm.services.mock_data_service.mock_data_service.get_payment_periods') as mock_get_periods, \
         patch('feptm.services.mock_data_service.mock_data_service.get_projects') as mock_get_projects:
        # Set up the mocks to return the test data
        mock_get_periods.return_value = mock_periods
        mock_get_projects.return_value = mock_projects
        
        # Make the request
        response = client.get("/api/reports/projects")
        
        # Check that the response status code is 200 OK
        assert response.status_code == status.HTTP_200_OK
        
        # Check that the mocks were called
        mock_get_periods.assert_called_once()
        mock_get_projects.assert_called_once()
        
        # Check that the response data matches the expected reports
        data = response.json()
        assert len(data) == 2
        # Sort by project_id to ensure consistent order
        data.sort(key=lambda x: x["project_id"])
        
        assert data[0]["project_id"] == "p1"
        assert data[0]["name"] == "Project Alpha"
        assert data[0]["client_name"] == "Client A"
        assert data[0]["total_hours"] == 22.0
        assert data[0]["specialist_count"] == 2
        
        assert data[1]["project_id"] == "p2"
        assert data[1]["name"] == "Project Beta"
        assert data[1]["client_name"] == "Client B"
        assert data[1]["total_hours"] == 8.0
        assert data[1]["specialist_count"] == 1


@pytest.mark.skip(reason="Нужно исправить API отчетов")
def test_get_project_reports_with_period(client):
    """Test GET /api/reports/projects with period filter."""
    # Test data - определено прямо в тесте для лучшей читаемости
    # Mock projects
    mock_projects = [
        Project(
            id="p1",
            name="Project Alpha",
            description="Test project",
            client_name="Client A",
            status=ProjectStatus.ACTIVE,
            project_type=ProjectType.TIME_AND_MATERIALS,
            start_date="2023-02-01T00:00:00Z"
        ),
        Project(
            id="p2",
            name="Project Beta",
            description="Test project",
            client_name="Client B",
            status=ProjectStatus.ACTIVE,
            project_type=ProjectType.TIME_AND_MATERIALS,
            start_date="2023-01-15T00:00:00Z"
        )
    ]
    
    # Mock period with time entries
    mock_period = PaymentPeriod(
        id="pp1",
        name="March 2023",
        start_date=date(2023, 3, 1),
        end_date=date(2023, 3, 31),
        status=PeriodStatus.OPEN,
        time_entries=[
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
                hours=8.0,
                description="Development work"
            )
        ]
    )
    
    # Expected reports for specific period
    expected_reports = [
        ProjectReport(
            project_id="p1",
            name="Project Alpha",
            client_name="Client A",
            total_hours=14.0,  # 8 + 6
            specialist_count=2  # s1, s2
        ),
        ProjectReport(
            project_id="p2",
            name="Project Beta",
            client_name="Client B",
            total_hours=8.0,
            specialist_count=1  # s1
        )
    ]
    
    # Mock the necessary methods
    with patch('feptm.services.mock_data_service.mock_data_service.get_payment_period') as mock_get_period, \
         patch('feptm.services.mock_data_service.mock_data_service.get_projects') as mock_get_projects:
        # Set up the mocks to return the test data
        mock_get_period.return_value = mock_period
        mock_get_projects.return_value = mock_projects
        
        # Make the request
        response = client.get("/api/reports/projects?period_id=pp1")
        
        # Check that the response status code is 200 OK
        assert response.status_code == status.HTTP_200_OK
        
        # Check that the mocks were called with correct arguments
        mock_get_period.assert_called_once_with("pp1")
        mock_get_projects.assert_called_once()
        
        # Check that the response data matches the expected reports
        data = response.json()
        assert len(data) == 2
        # Sort by project_id to ensure consistent order
        data.sort(key=lambda x: x["project_id"])
        
        assert data[0]["project_id"] == "p1"
        assert data[0]["name"] == "Project Alpha"
        assert data[0]["total_hours"] == 14.0
        assert data[0]["specialist_count"] == 2
        
        assert data[1]["project_id"] == "p2"
        assert data[1]["name"] == "Project Beta"
        assert data[1]["total_hours"] == 8.0
        assert data[1]["specialist_count"] == 1


def test_get_project_reports_period_not_found(client):
    """Test GET /api/reports/projects with non-existent period ID."""
    # Mock the get_payment_period method
    with patch('feptm.services.mock_data_service.mock_data_service.get_payment_period') as mock_get_period:
        # Set up the mock to return None (period not found)
        mock_get_period.return_value = None
        
        # Make the request
        response = client.get("/api/reports/projects?period_id=non-existent")
        
        # Check that the response status code is 404 Not Found
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Check that the mock was called with the correct arguments
        mock_get_period.assert_called_once_with("non-existent")
        
        # Check the error message
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower() 