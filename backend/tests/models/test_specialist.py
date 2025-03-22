"""Tests for the Specialist model."""

from datetime import datetime, timezone
import pytest
from pydantic import ValidationError

from feptm.models.specialist import Specialist, SpecialistRole


def test_specialist_role_enum():
    """Test SpecialistRole enum values."""
    # Test that all roles are defined correctly
    assert SpecialistRole.DEVELOPER.value == "Developer"
    assert SpecialistRole.QA.value == "QA"
    assert SpecialistRole.DESIGNER.value == "Designer"
    assert SpecialistRole.PROJECT_MANAGER.value == "Project Manager"
    assert SpecialistRole.DEVOPS.value == "DevOps"


def test_specialist_role_from_config(monkeypatch):
    """Test SpecialistRole.from_config method."""
    # Mock settings
    monkeypatch.setattr(
        "feptm.core.config.settings.SPECIALIST_ROLES",
        ["Developer", "QA"]
    )
    
    # Get roles from config
    roles = SpecialistRole.from_config()
    
    # Check that only roles in config are returned
    assert len(roles) == 2
    assert SpecialistRole.DEVELOPER in roles
    assert SpecialistRole.QA in roles
    assert SpecialistRole.DESIGNER not in roles
    assert SpecialistRole.PROJECT_MANAGER not in roles
    assert SpecialistRole.DEVOPS not in roles


def test_specialist_creation_with_valid_data():
    """Test creating a Specialist with valid data."""
    # Create a specialist
    specialist = Specialist(
        full_name="John Doe",
        email="john.doe@example.com",
        role=SpecialistRole.DEVELOPER,
        hourly_rate=50.0,
        hire_date=datetime(2023, 1, 15, tzinfo=timezone.utc)
    )
    
    # Check that the specialist was created with correct values
    assert specialist.full_name == "John Doe"
    assert specialist.email == "john.doe@example.com"
    assert specialist.role == SpecialistRole.DEVELOPER
    assert specialist.hourly_rate == 50.0
    assert specialist.active is True
    assert specialist.hire_date == datetime(2023, 1, 15, tzinfo=timezone.utc)
    assert specialist.leave_date is None
    assert specialist.id is not None  # Should have generated an ID


def test_specialist_creation_with_all_fields():
    """Test creating a Specialist with all fields specified."""
    # Create a specialist with all fields
    specialist = Specialist(
        id="test-id",
        full_name="Jane Smith",
        email="jane.smith@example.com",
        role=SpecialistRole.PROJECT_MANAGER,
        hourly_rate=60.0,
        active=False,
        hire_date=datetime(2022, 6, 1, tzinfo=timezone.utc),
        leave_date=datetime(2023, 6, 1, tzinfo=timezone.utc)
    )
    
    # Check that the specialist was created with correct values
    assert specialist.id == "test-id"
    assert specialist.full_name == "Jane Smith"
    assert specialist.email == "jane.smith@example.com"
    assert specialist.role == SpecialistRole.PROJECT_MANAGER
    assert specialist.hourly_rate == 60.0
    assert specialist.active is False
    assert specialist.hire_date == datetime(2022, 6, 1, tzinfo=timezone.utc)
    assert specialist.leave_date == datetime(2023, 6, 1, tzinfo=timezone.utc)


def test_specialist_invalid_email():
    """Test that invalid email raises ValidationError."""
    # Attempt to create a specialist with invalid email
    with pytest.raises(ValidationError) as exc_info:
        Specialist(
            full_name="John Doe",
            email="invalid-email",  # Invalid email format
            role=SpecialistRole.DEVELOPER,
            hourly_rate=50.0,
            hire_date=datetime(2023, 1, 15, tzinfo=timezone.utc)
        )
    
    # Check that the error message indicates email validation issue
    errors = exc_info.value.errors()
    assert any("email" in error["loc"] for error in errors)


def test_specialist_invalid_role():
    """Test that invalid role raises ValidationError."""
    # Attempt to create a specialist with invalid role
    with pytest.raises(ValidationError) as exc_info:
        Specialist(
            full_name="John Doe",
            email="john.doe@example.com",
            role="Invalid Role",  # Invalid role
            hourly_rate=50.0,
            hire_date=datetime(2023, 1, 15, tzinfo=timezone.utc)
        )
    
    # Check that the error message indicates role validation issue
    errors = exc_info.value.errors()
    assert any("role" in error["loc"] for error in errors)


def test_specialist_negative_hourly_rate():
    """Test that negative hourly rate is allowed but not recommended."""
    # Create a specialist with negative hourly rate
    specialist = Specialist(
        full_name="John Doe",
        email="john.doe@example.com",
        role=SpecialistRole.DEVELOPER,
        hourly_rate=-10.0,  # Negative hourly rate
        hire_date=datetime(2023, 1, 15, tzinfo=timezone.utc)
    )
    
    # Check that the specialist was created with negative hourly rate
    assert specialist.hourly_rate == -10.0


def test_specialist_missing_required_fields():
    """Test that missing required fields raises ValidationError."""
    # Attempt to create a specialist without required fields
    with pytest.raises(ValidationError) as exc_info:
        Specialist()
    
    # Check that the error message indicates missing required fields
    errors = exc_info.value.errors()
    missing_fields = [error["loc"][0] for error in errors]
    assert "full_name" in missing_fields
    assert "email" in missing_fields
    assert "role" in missing_fields
    assert "hourly_rate" in missing_fields
    assert "hire_date" in missing_fields 