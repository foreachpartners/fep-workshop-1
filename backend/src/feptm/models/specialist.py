"""Specialist model definitions."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from feptm.core.config import settings
from feptm.core.utils import generate_uuid


class SpecialistRole(str, Enum):
    """Enumeration for specialist roles."""
    
    DEVELOPER = "Developer"
    QA = "QA"
    DESIGNER = "Designer"
    PROJECT_MANAGER = "Project Manager"
    DEVOPS = "DevOps"
    
    @classmethod
    def from_config(cls) -> list["SpecialistRole"]:
        """Get roles from configuration.
        
        Returns:
            List of roles defined in configuration
        """
        return [role for role in cls if role.value in settings.SPECIALIST_ROLES]


class Specialist(BaseModel):
    """Specialist model representing a team member."""
    
    id: str = Field(default_factory=generate_uuid)
    full_name: str
    email: EmailStr
    role: SpecialistRole
    hourly_rate: float
    active: bool = True
    hire_date: datetime
    leave_date: Optional[datetime] = None
    
    class Config:
        """Model configuration."""
        
        json_schema_extra = {
            "example": {
                "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                "full_name": "John Doe",
                "email": "john.doe@example.com",
                "role": "Developer",
                "hourly_rate": 50.0,
                "active": True,
                "hire_date": "2023-01-15T00:00:00Z",
                "leave_date": None
            }
        } 