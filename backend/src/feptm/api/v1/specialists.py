"""API endpoints for specialists."""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional

from feptm.models import Specialist
from feptm.services.mock_data_service import mock_data_service

router = APIRouter()


@router.get("/", response_model=List[Specialist])
async def get_specialists(
    active: Optional[bool] = Query(None, description="Filter by active status"),
    role: Optional[str] = Query(None, description="Filter by role")
):
    """Get all specialists with optional filtering.
    
    Args:
        active: Filter by active status
        role: Filter by role
    
    Returns:
        List of specialists
    """
    filters = {}
    if active is not None:
        filters["active"] = active
    if role is not None:
        filters["role"] = role
        
    specialists = mock_data_service.get_filtered_data("specialists", filters)
    return specialists


@router.get("/{specialist_id}", response_model=Specialist)
async def get_specialist(
    specialist_id: str = Path(..., description="The ID of the specialist to get")
):
    """Get a specialist by ID.
    
    Args:
        specialist_id: ID of the specialist
    
    Returns:
        Specialist if found
        
    Raises:
        HTTPException: If specialist not found
    """
    specialist = mock_data_service.get_specialist(specialist_id)
    if specialist is None:
        raise HTTPException(status_code=404, detail=f"Specialist with ID {specialist_id} not found")
    return specialist 