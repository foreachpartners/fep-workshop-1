"""API endpoints for period management."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_periods():
    """Get all periods."""
    return {"message": "List of periods"} 