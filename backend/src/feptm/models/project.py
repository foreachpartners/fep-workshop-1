"""Project model definitions."""

from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field, HttpUrl

from feptm.core.utils import generate_uuid


class ProjectStatus(str, Enum):
    """Project status enumeration."""
    
    PLANNING = "Planning"
    ACTIVE = "Active"
    ON_HOLD = "On Hold"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class ProjectType(str, Enum):
    """Project type enumeration."""
    
    FIXED_PRICE = "Fixed Price"
    TIME_AND_MATERIALS = "Time and Materials"
    RETAINER = "Retainer"


class Project(BaseModel):
    """Project model representing a client project."""
    
    id: str = Field(default_factory=generate_uuid)
    name: str
    description: str
    client_name: str
    client_contact_email: Optional[str] = None
    client_contact_phone: Optional[str] = None
    status: ProjectStatus = ProjectStatus.PLANNING
    project_type: ProjectType = ProjectType.TIME_AND_MATERIALS
    timesheet_id: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    budget: Optional[float] = None
    repository_url: Optional[HttpUrl] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    specialist_ids: List[str] = Field(default_factory=list)
    
    class Config:
        """Model configuration."""
        
        json_schema_extra = {
            "example": {
                "id": "a47bc10b-58cc-4372-a567-0e02b2c3d123",
                "name": "E-Commerce Platform",
                "description": "Development of online store with payment integration",
                "client_name": "ABC Retail",
                "client_contact_email": "contact@abcretail.com",
                "client_contact_phone": "+1234567890",
                "status": "Active",
                "project_type": "Time and Materials",
                "timesheet_id": "1ZRXVYuJEStH4SFzDh78DcwTr90FG3gHJKL",
                "start_date": "2023-03-01T00:00:00Z",
                "end_date": "2023-12-31T00:00:00Z",
                "budget": 50000.0,
                "repository_url": "https://github.com/example/project",
                "created_at": "2023-02-15T12:00:00Z",
                "updated_at": "2023-06-20T15:30:00Z",
                "specialist_ids": [
                    "f47ac10b-58cc-4372-a567-0e02b2c3d479", 
                    "b17dc20a-47dd-5461-b678-1f13a3d2e568"
                ]
            }
        } 