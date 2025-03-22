"""Service for providing mock data for development and testing."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, TypeVar, Generic, Type, Union

from pydantic import BaseModel, parse_obj_as

from feptm.core.config import settings
from feptm.models import Specialist, Project, PaymentPeriod
from feptm.models.payment import TimeEntry

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class MockDataService(Generic[T]):
    """Service for working with mock data from JSON files."""

    def __init__(self):
        """Initialize the mock data service."""
        self.data_dir = Path(__file__).parent.parent / "data"
        self._specialists: Optional[List[Specialist]] = None
        self._projects: Optional[List[Project]] = None
        self._payment_periods: Optional[List[PaymentPeriod]] = None
        
        if not self.data_dir.exists():
            logger.warning(f"Mock data directory not found: {self.data_dir}")
    
    def _load_data(self, file_name: str, model_class: Type[T]) -> List[T]:
        """Load data from a JSON file and parse into model objects.
        
        Args:
            file_name: Name of the JSON file
            model_class: Model class to parse data into
        
        Returns:
            List of parsed model objects
        
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the data cannot be parsed
        """
        file_path = self.data_dir / file_name
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return parse_obj_as(List[model_class], data)
        except FileNotFoundError:
            logger.error(f"Mock data file not found: {file_path}")
            return []
        except Exception as e:
            logger.error(f"Error loading mock data from {file_path}: {e}")
            return []
    
    def get_specialists(self) -> List[Specialist]:
        """Get all specialists.
        
        Returns:
            List of specialists
        """
        if self._specialists is None:
            self._specialists = self._load_data("specialists.json", Specialist)
        return self._specialists
    
    def get_specialist(self, specialist_id: str) -> Optional[Specialist]:
        """Get a specialist by ID.
        
        Args:
            specialist_id: ID of the specialist
        
        Returns:
            Specialist if found, None otherwise
        """
        specialists = self.get_specialists()
        for specialist in specialists:
            if specialist.id == specialist_id:
                return specialist
        return None
    
    def get_projects(self) -> List[Project]:
        """Get all projects.
        
        Returns:
            List of projects
        """
        if self._projects is None:
            self._projects = self._load_data("projects.json", Project)
        return self._projects
    
    def get_project(self, project_id: str) -> Optional[Project]:
        """Get a project by ID.
        
        Args:
            project_id: ID of the project
        
        Returns:
            Project if found, None otherwise
        """
        projects = self.get_projects()
        for project in projects:
            if project.id == project_id:
                return project
        return None
    
    def get_payment_periods(self) -> List[PaymentPeriod]:
        """Get all payment periods.
        
        Returns:
            List of payment periods
        """
        if self._payment_periods is None:
            self._payment_periods = self._load_data("payment_periods.json", PaymentPeriod)
        return self._payment_periods
    
    def get_payment_period(self, period_id: str) -> Optional[PaymentPeriod]:
        """Get a payment period by ID.
        
        Args:
            period_id: ID of the payment period
        
        Returns:
            PaymentPeriod if found, None otherwise
        """
        periods = self.get_payment_periods()
        for period in periods:
            if period.id == period_id:
                return period
        return None
    
    def get_time_entries(self, 
                       specialist_id: Optional[str] = None, 
                       project_id: Optional[str] = None,
                       start_date: Optional[datetime] = None,
                       end_date: Optional[datetime] = None) -> List[TimeEntry]:
        """Get time entries with optional filtering.
        
        Args:
            specialist_id: Filter by specialist ID
            project_id: Filter by project ID
            start_date: Filter entries after this date
            end_date: Filter entries before this date
        
        Returns:
            List of time entries matching the filters
        """
        periods = self.get_payment_periods()
        result: List[TimeEntry] = []
        
        for period in periods:
            for entry in period.time_entries:
                if (specialist_id is None or entry.specialist_id == specialist_id) and \
                   (project_id is None or entry.project_id == project_id) and \
                   (start_date is None or entry.date >= start_date) and \
                   (end_date is None or entry.date <= end_date):
                    result.append(entry)
        
        return result
    
    def get_filtered_data(self, 
                        data_type: str, 
                        filters: Optional[Dict[str, Any]] = None) -> List[Union[Specialist, Project, PaymentPeriod, TimeEntry]]:
        """Get data of specified type with optional filtering.
        
        Args:
            data_type: Type of data to get ('specialists', 'projects', 'payment_periods', 'time_entries')
            filters: Filters to apply to the data
        
        Returns:
            List of data items matching the filters
            
        Raises:
            ValueError: If data_type is invalid
        """
        filters = filters or {}
        
        if data_type == "specialists":
            data = self.get_specialists()
            # Simple filtering for demonstration
            if "active" in filters:
                data = [s for s in data if s.active == filters["active"]]
            if "role" in filters:
                data = [s for s in data if s.role.value == filters["role"]]
            return data
            
        elif data_type == "projects":
            data = self.get_projects()
            if "status" in filters:
                data = [p for p in data if p.status.value == filters["status"]]
            if "project_type" in filters:
                data = [p for p in data if p.project_type.value == filters["project_type"]]
            return data
            
        elif data_type == "payment_periods":
            data = self.get_payment_periods()
            if "status" in filters:
                data = [p for p in data if p.status.value == filters["status"]]
            return data
            
        elif data_type == "time_entries":
            return self.get_time_entries(
                specialist_id=filters.get("specialist_id"),
                project_id=filters.get("project_id"),
                start_date=filters.get("start_date"),
                end_date=filters.get("end_date")
            )
            
        else:
            raise ValueError(f"Invalid data type: {data_type}")


# Singleton instance for easy access
mock_data_service = MockDataService() 