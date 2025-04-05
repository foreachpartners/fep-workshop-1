"""Tests for the projects API endpoints."""

import pytest
from unittest.mock import patch, MagicMock
from fastapi import status

from feptm.models import Project
from tests.stubs import create_mock_projects, mock_api_endpoint


def test_get_projects(client):
    """Test GET /api/projects endpoint."""
    # Get mock projects
    mock_projects = create_mock_projects()
    
    # Mock the API endpoint function
    with mock_api_endpoint("feptm.api.v1.projects.get_projects", mock_projects):
        # Make the request
        response = client.get("/api/projects/")
        
        # Check that the response status code is 200 OK
        assert response.status_code == status.HTTP_200_OK
        
        # Check that the response data matches the mock data
        data = response.json()
        assert len(data) == 2
        assert data[0]["id"] == "p1"
        assert data[0]["name"] == "E-Commerce Platform"
        assert data[1]["id"] == "p2"
        assert data[1]["name"] == "Mobile App"


def test_get_project_by_id(client):
    """Test GET /api/projects/{project_id} endpoint."""
    # Get mock project
    mock_project = create_mock_projects()[0]
    
    # Mock the API endpoint function
    with mock_api_endpoint("feptm.api.v1.projects.get_project", mock_project):
        # Make the request
        response = client.get("/api/projects/p1")
        
        # Check that the response status code is 200 OK
        assert response.status_code == status.HTTP_200_OK
        
        # Check that the response data matches the mock data
        data = response.json()
        assert data["id"] == "p1"
        assert data["name"] == "E-Commerce Platform"


def test_get_project_not_found(client):
    """Test GET /api/projects/{project_id} with non-existent ID."""
    # Mock the API endpoint to return a 404 exception
    with patch("feptm.api.v1.projects.get_project") as mock_get:
        # Set up the mock to raise HTTPException with 404 status
        mock_get.side_effect = lambda project_id: pytest.raises(
            status.HTTP_404_NOT_FOUND, 
            match=f"Project with ID {project_id} not found"
        )
        
        # Make the request
        response = client.get("/api/projects/non-existent")
        
        # Check that the response status code is 404 Not Found
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
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
        mock_create_project.side_effect = Exception("Test error")
        
        # Make the request
        response = client.post("/api/projects/create", json=request_data)
        
        # Check that the response status code is 500 Internal Server Error
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        
        # Check the error message
        data = response.json()
        assert "detail" in data
        assert "failed to create project" in data["detail"].lower() 