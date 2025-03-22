"""Payment model definitions."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field

from feptm.core.utils import generate_uuid, format_date_range


class PaymentStatus(str, Enum):
    """Payment status enumeration."""
    
    DRAFT = "Draft"
    SUBMITTED = "Submitted"
    APPROVED = "Approved"
    PAID = "Paid"
    REJECTED = "Rejected"


class PeriodStatus(str, Enum):
    """Payment period status enumeration."""
    
    OPEN = "Open"
    CLOSED = "Closed"
    LOCKED = "Locked"


class TimeEntry(BaseModel):
    """Time entry for specialist work."""
    
    id: str = Field(default_factory=generate_uuid)
    specialist_id: str
    project_id: str
    date: datetime
    hours: float
    description: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PaymentPeriod(BaseModel):
    """Payment period for a group of time entries."""
    
    id: str = Field(default_factory=generate_uuid)
    name: Optional[str] = None
    start_date: datetime
    end_date: datetime
    status: Union[PaymentStatus, PeriodStatus] = PaymentStatus.DRAFT
    report_id: Optional[str] = None
    time_entries: List[TimeEntry] = Field(default_factory=list)
    specialist_totals: Dict[str, float] = Field(default_factory=dict)
    project_totals: Dict[str, float] = Field(default_factory=dict)
    total_hours: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def __init__(self, **data):
        """Initialize the payment period with an auto-generated name if not provided."""
        if "start_date" in data and "end_date" in data and "name" not in data:
            data["name"] = format_date_range(data["start_date"], data["end_date"])
        super().__init__(**data)
    
    def add_time_entry(self, time_entry: TimeEntry) -> None:
        """Add a time entry to the payment period.
        
        Args:
            time_entry: Time entry to add
        """
        self.time_entries.append(time_entry)
        self._update_totals(time_entry)
        self.updated_at = datetime.utcnow()
    
    def _update_totals(self, time_entry: TimeEntry) -> None:
        """Update totals based on a new time entry.
        
        Args:
            time_entry: Time entry to use for updating totals
        """
        # Update specialist totals
        specialist_id = time_entry.specialist_id
        self.specialist_totals[specialist_id] = self.specialist_totals.get(specialist_id, 0.0) + time_entry.hours
        
        # Update project totals
        project_id = time_entry.project_id
        self.project_totals[project_id] = self.project_totals.get(project_id, 0.0) + time_entry.hours
        
        # Update total hours
        self.total_hours += time_entry.hours
    
    class Config:
        """Model configuration."""
        
        json_schema_extra = {
            "example": {
                "id": "d47ef20c-69dd-4583-b789-2f24b4e5f678",
                "name": "Jun - Jul 2023",
                "start_date": "2023-06-01T00:00:00Z",
                "end_date": "2023-07-31T23:59:59Z",
                "status": "Approved",
                "report_id": "1ABCDEfghIJklMNopQRst-uvWXyz12345678",
                "time_entries": [
                    {
                        "id": "e58fg30d-70ee-5694-c890-3g35c5f6h789",
                        "specialist_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                        "project_id": "a47bc10b-58cc-4372-a567-0e02b2c3d123",
                        "date": "2023-06-15T00:00:00Z",
                        "hours": 8.0,
                        "description": "API development and testing",
                        "created_at": "2023-06-15T19:00:00Z",
                        "updated_at": "2023-06-15T19:00:00Z"
                    }
                ],
                "specialist_totals": {
                    "f47ac10b-58cc-4372-a567-0e02b2c3d479": 160.0
                },
                "project_totals": {
                    "a47bc10b-58cc-4372-a567-0e02b2c3d123": 160.0
                },
                "total_hours": 160.0,
                "created_at": "2023-06-01T00:00:00Z",
                "updated_at": "2023-08-01T10:30:00Z"
            }
        } 