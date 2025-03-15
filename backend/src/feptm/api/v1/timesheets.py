"""API endpoints for timesheet management."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_timesheets():
    """Get all timesheets."""
    return {"message": "List of timesheets"} 