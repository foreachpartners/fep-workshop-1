"""API endpoints for timesheets."""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from typing import List, Optional

from feptm.models.payment import TimeEntry
from feptm.services.mock_data_service import mock_data_service

router = APIRouter()


@router.get("/time-entries", response_model=List[TimeEntry])
async def get_time_entries(
    specialist_id: Optional[str] = Query(None, description="Filter by specialist ID"),
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    start_date: Optional[datetime] = Query(None, description="Filter entries after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter entries before this date")
):
    """Get time entries with optional filtering.
    
    Args:
        specialist_id: Filter by specialist ID
        project_id: Filter by project ID
        start_date: Filter entries after this date
        end_date: Filter entries before this date
    
    Returns:
        List of time entries matching the filters
    """
    filters = {
        "specialist_id": specialist_id,
        "project_id": project_id,
        "start_date": start_date,
        "end_date": end_date
    }
    
    # Remove None values
    filters = {k: v for k, v in filters.items() if v is not None}
    
    entries = mock_data_service.get_filtered_data("time_entries", filters)
    return entries 