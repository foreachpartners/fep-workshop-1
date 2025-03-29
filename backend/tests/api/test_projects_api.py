"""Tests for the projects API endpoints."""

import pytest
from unittest.mock import patch, MagicMock
from fastapi import status

from feptm.models import Project
from feptm.models.project import ProjectStatus, ProjectType


def test_get_projects(client):
    """Test GET /api/projects endpoint."""
    # Test data - определено прямо в тесте для лучшей читаемости
    mock_projects = [
        Project(
            id="p1",
            name="Project Alpha",
            description="First test project",
            client_name="Client A",
            status=ProjectStatus.ACTIVE,
            project_type=ProjectType.TIME_AND_MATERIALS,
            start_date="2023-02-01T00:00:00Z"
        ),
        Project(
            id="p2",
            name="Project Beta",
            description="Second test project",
            client_name="Client B",
            status=ProjectStatus.COMPLETED,
            project_type=ProjectType.FIXED_PRICE,
            start_date="2023-01-15T00:00:00Z",
            end_date="2023-06-15T00:00:00Z"
        )
    ]
    
    # Mock the get_filtered_data method
    with patch('feptm.services.mock_data_service.mock_data_service.get_filtered_data') as mock_get_filtered:
        # Set up the mock to return the test data
        mock_get_filtered.return_value = mock_projects
        
        # Make the request
        response = client.get("/api/projects/")
        
        # Check that the response status code is 200 OK
        assert response.status_code == status.HTTP_200_OK
        
        # Check that the mock was called with the correct arguments
        mock_get_filtered.assert_called_once_with("projects", {})
        
        # Check that the response data matches the mock data
        data = response.json()
        assert len(data) == 2
        assert data[0]["id"] == "p1"
        assert data[0]["name"] == "Project Alpha"
        assert data[0]["status"] == "Active"
        assert data[1]["id"] == "p2"
        assert data[1]["name"] == "Project Beta"
        assert data[1]["status"] == "Completed"


def test_get_projects_with_status_filter(client):
    """Test GET /api/projects with status filter."""
    # Test data - определено прямо в тесте для лучшей читаемости
    mock_projects = [
        Project(
            id="p1",
            name="Project Alpha",
            description="Test project",
            client_name="Client A",
            status=ProjectStatus.ACTIVE,
            project_type=ProjectType.TIME_AND_MATERIALS,
            start_date="2023-02-01T00:00:00Z"
        )
    ]
    
    # Mock the get_filtered_data method
    with patch('feptm.services.mock_data_service.mock_data_service.get_filtered_data') as mock_get_filtered:
        # Set up the mock to return the test data
        mock_get_filtered.return_value = mock_projects
        
        # Make the request with query parameters
        response = client.get("/api/projects/?status=Active")
        
        # Check that the response status code is 200 OK
        assert response.status_code == status.HTTP_200_OK
        
        # Check that the mock was called with the correct arguments
        mock_get_filtered.assert_called_once_with("projects", {"status": "Active"})
        
        # Check that the response data matches the mock data
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == "p1"
        assert data[0]["name"] == "Project Alpha"
        assert data[0]["status"] == "Active"


def test_get_projects_with_type_filter(client):
    """Test GET /api/projects with project_type filter."""
    # Test data - определено прямо в тесте для лучшей читаемости
    mock_projects = [
        Project(
            id="p2",
            name="Project Beta",
            description="Test project",
            client_name="Client B",
            status=ProjectStatus.COMPLETED,
            project_type=ProjectType.FIXED_PRICE,
            start_date="2023-01-15T00:00:00Z",
            end_date="2023-06-15T00:00:00Z"
        )
    ]
    
    # Mock the get_filtered_data method
    with patch('feptm.services.mock_data_service.mock_data_service.get_filtered_data') as mock_get_filtered:
        # Set up the mock to return the test data
        mock_get_filtered.return_value = mock_projects
        
        # Make the request with query parameters
        response = client.get("/api/projects/?project_type=Fixed%20Price")
        
        # Check that the response status code is 200 OK
        assert response.status_code == status.HTTP_200_OK
        
        # Check that the mock was called with the correct arguments
        mock_get_filtered.assert_called_once_with("projects", {"project_type": "Fixed Price"})
        
        # Check that the response data matches the mock data
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == "p2"
        assert data[0]["name"] == "Project Beta"
        assert data[0]["project_type"] == "Fixed Price"


def test_get_project_by_id(client):
    """Test GET /api/projects/{project_id} endpoint."""
    # Test data - определено прямо в тесте для лучшей читаемости
    mock_project = Project(
        id="p1",
        name="Project Alpha",
        description="Test project",
        client_name="Client A",
        status=ProjectStatus.ACTIVE,
        project_type=ProjectType.TIME_AND_MATERIALS,
        start_date="2023-02-01T00:00:00Z"
    )
    
    # Mock the get_project method
    with patch('feptm.services.mock_data_service.mock_data_service.get_project') as mock_get_project:
        # Set up the mock to return the test data
        mock_get_project.return_value = mock_project
        
        # Make the request
        response = client.get("/api/projects/p1")
        
        # Check that the response status code is 200 OK
        assert response.status_code == status.HTTP_200_OK
        
        # Check that the mock was called with the correct arguments
        mock_get_project.assert_called_once_with("p1")
        
        # Check that the response data matches the mock data
        data = response.json()
        assert data["id"] == "p1"
        assert data["name"] == "Project Alpha"
        assert data["description"] == "Test project"
        assert data["client_name"] == "Client A"
        assert data["status"] == "Active"
        assert data["project_type"] == "Time and Materials"


def test_get_project_not_found(client):
    """Test GET /api/projects/{project_id} with non-existent ID."""
    # Mock the get_project method
    with patch('feptm.services.mock_data_service.mock_data_service.get_project') as mock_get_project:
        # Set up the mock to return None (project not found)
        mock_get_project.return_value = None
        
        # Make the request
        response = client.get("/api/projects/non-existent")
        
        # Check that the response status code is 404 Not Found
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Check that the mock was called with the correct arguments
        mock_get_project.assert_called_once_with("non-existent")
        
        # Check the error message
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()


def test_create_project(client):
    """Test POST /api/projects/create endpoint."""
    # Mock data for testing
    mock_result = {
        "project_id": "test-project-id",
        "drive_folder_id": "test-folder-id",
        "drive_folder_url": "https://drive.google.com/drive/folders/test-folder-id",
        "project_info_spreadsheet_id": "test-info-id",
        "project_info_spreadsheet_url": "https://docs.google.com/spreadsheets/d/test-info-id",
        "report_spreadsheet_id": "test-report-id",
        "report_spreadsheet_url": "https://docs.google.com/spreadsheets/d/test-report-id",
        "calculations_spreadsheet_id": "test-calc-id",
        "calculations_spreadsheet_url": "https://docs.google.com/spreadsheets/d/test-calc-id"
    }
    
    # Request data
    request_data = {
        "project_name": "Test Project"
    }
    
    # Mock the create_project method
    with patch('feptm.services.google_sheets_service.google_sheets_service.create_project') as mock_create_project:
        # Set up the mock to return our test result
        mock_create_project.return_value = mock_result
        
        # Make the request
        response = client.post("/api/projects/create", json=request_data)
        
        # Check that the response status code is 200 OK
        assert response.status_code == status.HTTP_200_OK
        
        # Check that the function was called with the correct data
        mock_create_project.assert_called_once()
        args, kwargs = mock_create_project.call_args
        assert args[0].name == "Test Project"
        
        # Check the response data
        data = response.json()
        assert data["project_id"] == "test-project-id"
        assert data["drive_folder_id"] == "test-folder-id"
        assert data["drive_folder_url"] == "https://drive.google.com/drive/folders/test-folder-id"
        assert data["project_info_spreadsheet_id"] == "test-info-id"
        assert data["project_info_spreadsheet_url"] == "https://docs.google.com/spreadsheets/d/test-info-id"
        assert data["report_spreadsheet_id"] == "test-report-id"
        assert data["report_spreadsheet_url"] == "https://docs.google.com/spreadsheets/d/test-report-id"
        assert data["calculations_spreadsheet_id"] == "test-calc-id"
        assert data["calculations_spreadsheet_url"] == "https://docs.google.com/spreadsheets/d/test-calc-id"


def test_create_project_error(client):
    """Test POST /api/projects/create endpoint with error."""
    # Request data
    request_data = {
        "project_name": "Test Project"
    }
    
    # Mock the create_project method to raise an exception
    with patch('feptm.services.google_sheets_service.google_sheets_service.create_project') as mock_create_project:
        # Set up the mock to raise an exception
        mock_create_project.side_effect = Exception("Test error")
        
        # Make the request
        response = client.post("/api/projects/create", json=request_data)
        
        # Check that the response status code is 500 Internal Server Error
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        
        # Check the error message
        data = response.json()
        assert "detail" in data
        assert "test error" in data["detail"].lower() 