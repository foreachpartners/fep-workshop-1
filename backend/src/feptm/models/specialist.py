"""Specialist model definitions."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, computed_field


class Specialist(BaseModel):
    """Specialist model representing a team member on a project."""

    name: str
    role: str
    project: Optional[str] = None
    email: Optional[str] = None
    internal_rate: Decimal = Decimal("0")
    external_rate: Decimal = Decimal("0")  # Ставка для клиента
    date_added: Optional[datetime] = Field(default_factory=datetime.utcnow)
    timesheet_id: Optional[str] = None

    @computed_field
    def timesheet_url(self) -> Optional[str]:
        """Get the timesheet URL."""
        if not self.timesheet_id:
            return None
        return f"https://docs.google.com/spreadsheets/d/{self.timesheet_id}"

    @computed_field
    def has_timesheet(self) -> bool:
        """Check if specialist has a timesheet."""
        return self.timesheet_id is not None

    class Config:
        """Model configuration."""

        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "role": "Developer",
                "project": "E-Commerce Platform",
                "email": "john.doe@example.com",
                "internal_rate": "20.00",
                "external_rate": "25.00",
                "date_added": "2023-02-15T12:00:00Z",
                "timesheet_id": "1abCdEfGhIjKlMnOpQrStUvWxYz",
            }
        }
