"""Tests for the Project model."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from feptm.models.project import Project


def test_project_creation_with_minimal_fields():
    """Test creating a Project with minimal required fields."""
    # Create a project with only required fields
    project = Project(name="Test Project")
    
    # Check that the project was created with correct values
    assert project.name == "Test Project"
    
    # Check default values
    assert project.drive_folder_id is None
    assert project.project_info_spreadsheet_id is None
    assert project.report_spreadsheet_id is None
    assert project.calculations_spreadsheet_id is None
    assert project.id is not None  # Should have generated an ID
    assert isinstance(project.created, datetime)
    assert isinstance(project.modified, datetime)


def test_project_creation_with_all_fields():
    """Test creating a Project with all fields specified."""
    # Test data
    created = datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
    modified = datetime(2023, 1, 2, 15, 30, 0, tzinfo=timezone.utc)
    
    # Create a project with all fields
    project = Project(
        id="test-id",
        name="Complete Project",
        drive_folder_id="folder-123",
        project_info_spreadsheet_id="info-sheet-123",
        report_spreadsheet_id="report-sheet-123",
        calculations_spreadsheet_id="calc-sheet-123",
        created=created,
        modified=modified
    )
    
    # Check that the project was created with correct values
    assert project.id == "test-id"
    assert project.name == "Complete Project"
    assert project.drive_folder_id == "folder-123"
    assert project.project_info_spreadsheet_id == "info-sheet-123"
    assert project.report_spreadsheet_id == "report-sheet-123"
    assert project.calculations_spreadsheet_id == "calc-sheet-123"
    assert project.created == created
    assert project.modified == modified
    
    # Check computed fields
    assert project.drive_folder_url == "https://drive.google.com/drive/folders/folder-123"
    assert project.project_info_spreadsheet_url == "https://docs.google.com/spreadsheets/d/info-sheet-123"
    assert project.report_spreadsheet_url == "https://docs.google.com/spreadsheets/d/report-sheet-123"
    assert project.calculations_spreadsheet_url == "https://docs.google.com/spreadsheets/d/calc-sheet-123"


def test_project_missing_required_fields():
    """Test that missing required fields raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        Project()
    
    # Check that the error message indicates missing required fields
    errors = exc_info.value.errors()
    missing_fields = [error["loc"][0] for error in errors]
    assert "name" in missing_fields


def test_project_computed_urls_with_none_ids():
    """Test that computed URLs return None when IDs are None."""
    project = Project(name="Test Project")
    
    assert project.drive_folder_url is None
    assert project.project_info_spreadsheet_url is None
    assert project.report_spreadsheet_url is None
    assert project.calculations_spreadsheet_url is None 