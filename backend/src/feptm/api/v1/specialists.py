"""API endpoints for specialist management."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_specialists():
    """Get all specialists."""
    return {"message": "List of specialists"} 