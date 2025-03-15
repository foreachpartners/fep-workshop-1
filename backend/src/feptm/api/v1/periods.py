"""API endpoints for payment periods."""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional

from feptm.models import PaymentPeriod
from feptm.models.payment import TimeEntry
from feptm.services.mock_data_service import mock_data_service

router = APIRouter()


@router.get("/", response_model=List[PaymentPeriod])
async def get_payment_periods(
    status: Optional[str] = Query(None, description="Filter by status")
):
    """Get all payment periods with optional filtering.
    
    Args:
        status: Filter by payment status
    
    Returns:
        List of payment periods
    """
    filters = {}
    if status is not None:
        filters["status"] = status
        
    periods = mock_data_service.get_filtered_data("payment_periods", filters)
    return periods


@router.get("/{period_id}", response_model=PaymentPeriod)
async def get_payment_period(
    period_id: str = Path(..., description="The ID of the payment period to get")
):
    """Get a payment period by ID.
    
    Args:
        period_id: ID of the payment period
    
    Returns:
        PaymentPeriod if found
        
    Raises:
        HTTPException: If payment period not found
    """
    period = mock_data_service.get_payment_period(period_id)
    if period is None:
        raise HTTPException(status_code=404, detail=f"Payment period with ID {period_id} not found")
    return period


@router.get("/{period_id}/time-entries", response_model=List[TimeEntry])
async def get_period_time_entries(
    period_id: str = Path(..., description="The ID of the payment period"),
    specialist_id: Optional[str] = Query(None, description="Filter by specialist ID"),
    project_id: Optional[str] = Query(None, description="Filter by project ID")
):
    """Get time entries for a payment period with optional filtering.
    
    Args:
        period_id: ID of the payment period
        specialist_id: Filter by specialist ID
        project_id: Filter by project ID
    
    Returns:
        List of time entries
        
    Raises:
        HTTPException: If payment period not found
    """
    period = mock_data_service.get_payment_period(period_id)
    if period is None:
        raise HTTPException(status_code=404, detail=f"Payment period with ID {period_id} not found")
    
    # Filter time entries if needed
    entries = period.time_entries
    if specialist_id is not None:
        entries = [e for e in entries if e.specialist_id == specialist_id]
    if project_id is not None:
        entries = [e for e in entries if e.project_id == project_id]
        
    return entries 