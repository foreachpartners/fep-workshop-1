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