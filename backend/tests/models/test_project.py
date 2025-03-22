"""Tests for the Project model."""

from datetime import datetime, timezone
from typing import List

import pytest
from pydantic import ValidationError, HttpUrl

from feptm.models.project import Project, ProjectStatus, ProjectType


def test_project_status_enum():
    """Test ProjectStatus enum values."""
    assert ProjectStatus.PLANNING.value == "Planning"
    assert ProjectStatus.ACTIVE.value == "Active"
    assert ProjectStatus.ON_HOLD.value == "On Hold"
    assert ProjectStatus.COMPLETED.value == "Completed"
    assert ProjectStatus.CANCELLED.value == "Cancelled"


def test_project_type_enum():
    """Test ProjectType enum values."""
    assert ProjectType.FIXED_PRICE.value == "Fixed Price"
    assert ProjectType.TIME_AND_MATERIALS.value == "Time and Materials"
    assert ProjectType.RETAINER.value == "Retainer"


def test_project_creation_with_minimal_fields():
    """Test creating a Project with minimal required fields."""
    # Create a project with only required fields
    project = Project(
        name="Test Project",
        description="A test project",
        client_name="Test Client",
        start_date=datetime(2023, 1, 1, tzinfo=timezone.utc)
    )
    
    # Check that the project was created with correct values
    assert project.name == "Test Project"
    assert project.description == "A test project"
    assert project.client_name == "Test Client"
    assert project.start_date == datetime(2023, 1, 1, tzinfo=timezone.utc)
    
    # Check default values
    assert project.status == ProjectStatus.PLANNING
    assert project.project_type == ProjectType.TIME_AND_MATERIALS
    assert project.client_contact_email is None
    assert project.client_contact_phone is None
    assert project.timesheet_id is None
    assert project.end_date is None
    assert project.budget is None
    assert project.repository_url is None
    assert project.specialist_ids == []
    assert project.id is not None  # Should have generated an ID
    assert isinstance(project.created_at, datetime)
    assert isinstance(project.updated_at, datetime)


def test_project_creation_with_all_fields():
    """Test creating a Project with all fields specified."""
    # Test data
    specialist_ids: List[str] = ["spec-1", "spec-2"]
    start_date = datetime(2023, 1, 1, tzinfo=timezone.utc)
    end_date = datetime(2023, 12, 31, tzinfo=timezone.utc)
    created_at = datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
    updated_at = datetime(2023, 1, 2, 15, 30, 0, tzinfo=timezone.utc)
    
    # Create a project with all fields
    project = Project(
        id="test-id",
        name="Complete Project",
        description="A project with all fields",
        client_name="Complete Client",
        client_contact_email="contact@example.com",
        client_contact_phone="+1234567890",
        status=ProjectStatus.ACTIVE,
        project_type=ProjectType.FIXED_PRICE,
        timesheet_id="sheet-id-123",
        start_date=start_date,
        end_date=end_date,
        budget=50000.0,
        repository_url="https://github.com/example/project",
        created_at=created_at,
        updated_at=updated_at,
        specialist_ids=specialist_ids
    )
    
    # Check that the project was created with correct values
    assert project.id == "test-id"
    assert project.name == "Complete Project"
    assert project.description == "A project with all fields"
    assert project.client_name == "Complete Client"
    assert project.client_contact_email == "contact@example.com"
    assert project.client_contact_phone == "+1234567890"
    assert project.status == ProjectStatus.ACTIVE
    assert project.project_type == ProjectType.FIXED_PRICE
    assert project.timesheet_id == "sheet-id-123"
    assert project.start_date == start_date
    assert project.end_date == end_date
    assert project.budget == 50000.0
    assert str(project.repository_url) == "https://github.com/example/project"
    assert project.created_at == created_at
    assert project.updated_at == updated_at
    assert project.specialist_ids == specialist_ids


def test_project_invalid_repository_url():
    """Test that invalid repository URL raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        Project(
            name="Test Project",
            description="A test project",
            client_name="Test Client",
            start_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
            repository_url="invalid-url"  # Invalid URL format
        )
    
    # Check that the error message indicates repository URL validation issue
    errors = exc_info.value.errors()
    assert any("repository_url" in str(error["loc"]) for error in errors)


def test_project_invalid_status():
    """Test that invalid status raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        Project(
            name="Test Project",
            description="A test project",
            client_name="Test Client",
            start_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
            status="Invalid Status"  # Invalid status
        )
    
    # Check that the error message indicates status validation issue
    errors = exc_info.value.errors()
    assert any("status" in error["loc"] for error in errors)


def test_project_invalid_project_type():
    """Test that invalid project type raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        Project(
            name="Test Project",
            description="A test project",
            client_name="Test Client",
            start_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
            project_type="Invalid Type"  # Invalid project type
        )
    
    # Check that the error message indicates project type validation issue
    errors = exc_info.value.errors()
    assert any("project_type" in error["loc"] for error in errors)


def test_project_missing_required_fields():
    """Test that missing required fields raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        Project()
    
    # Check that the error message indicates missing required fields
    errors = exc_info.value.errors()
    missing_fields = [error["loc"][0] for error in errors]
    assert "name" in missing_fields
    assert "description" in missing_fields
    assert "client_name" in missing_fields
    assert "start_date" in missing_fields


def test_project_negative_budget():
    """Test that negative budget is allowed."""
    project = Project(
        name="Test Project",
        description="A test project",
        client_name="Test Client",
        start_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
        budget=-5000.0  # Negative budget
    )
    
    # Check that the project was created with negative budget
    assert project.budget == -5000.0 