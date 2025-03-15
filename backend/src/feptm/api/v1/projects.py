"""API endpoints for project management."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_projects():
    """Get all projects."""
    return {"message": "List of projects"} 