"""API endpoints for report management."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_reports():
    """Get all reports."""
    return {"message": "List of reports"} 