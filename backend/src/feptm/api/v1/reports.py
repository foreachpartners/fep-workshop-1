"""API endpoints for reports."""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import Dict, List, Optional

from pydantic import BaseModel

from feptm.services.mock_data_service import mock_data_service

router = APIRouter()


class SpecialistReport(BaseModel):
    """Model for specialist report data."""
    
    specialist_id: str
    full_name: str
    role: str
    total_hours: float
    hourly_rate: float
    total_amount: float


class ProjectReport(BaseModel):
    """Model for project report data."""
    
    project_id: str
    name: str
    client_name: str
    total_hours: float
    specialist_count: int


@router.get("/specialists", response_model=List[SpecialistReport])
async def get_specialist_reports(
    period_id: Optional[str] = Query(None, description="Filter by payment period ID")
):
    """Get specialist reports with optional filtering.
    
    Args:
        period_id: Filter by payment period ID
    
    Returns:
        List of specialist reports
    """
    # Get the relevant payment period
    if period_id:
        period = mock_data_service.get_payment_period(period_id)
        if period is None:
            raise HTTPException(status_code=404, detail=f"Payment period with ID {period_id} not found")
        periods = [period]
    else:
        periods = mock_data_service.get_payment_periods()
    
    # Get all specialists
    specialists = mock_data_service.get_specialists()
    specialist_map = {s.id: s for s in specialists}
    
    # Prepare report data
    report_data: Dict[str, SpecialistReport] = {}
    
    for period in periods:
        for specialist_id, hours in period.specialist_totals.items():
            if specialist_id in specialist_map:
                specialist = specialist_map[specialist_id]
                if specialist_id not in report_data:
                    report_data[specialist_id] = SpecialistReport(
                        specialist_id=specialist_id,
                        full_name=specialist.full_name,
                        role=specialist.role.value,
                        total_hours=0,
                        hourly_rate=specialist.hourly_rate,
                        total_amount=0
                    )
                
                report_data[specialist_id].total_hours += hours
                report_data[specialist_id].total_amount = report_data[specialist_id].total_hours * specialist.hourly_rate
    
    return list(report_data.values())


@router.get("/projects", response_model=List[ProjectReport])
async def get_project_reports(
    period_id: Optional[str] = Query(None, description="Filter by payment period ID")
):
    """Get project reports with optional filtering.
    
    Args:
        period_id: Filter by payment period ID
    
    Returns:
        List of project reports
    """
    # Get the relevant payment period
    if period_id:
        period = mock_data_service.get_payment_period(period_id)
        if period is None:
            raise HTTPException(status_code=404, detail=f"Payment period with ID {period_id} not found")
        periods = [period]
    else:
        periods = mock_data_service.get_payment_periods()
    
    # Get all projects
    projects = mock_data_service.get_projects()
    project_map = {p.id: p for p in projects}
    
    # Prepare report data
    report_data: Dict[str, ProjectReport] = {}
    
    for period in periods:
        # Count specialists per project in this period
        specialists_per_project: Dict[str, set] = {}
        
        for entry in period.time_entries:
            project_id = entry.project_id
            if project_id not in specialists_per_project:
                specialists_per_project[project_id] = set()
            specialists_per_project[project_id].add(entry.specialist_id)
        
        # Update report data
        for project_id, hours in period.project_totals.items():
            if project_id in project_map:
                project = project_map[project_id]
                if project_id not in report_data:
                    report_data[project_id] = ProjectReport(
                        project_id=project_id,
                        name=project.name,
                        client_name=project.client_name,
                        total_hours=0,
                        specialist_count=0
                    )
                
                report_data[project_id].total_hours += hours
                report_data[project_id].specialist_count = len(specialists_per_project.get(project_id, set()))
    
    return list(report_data.values()) 