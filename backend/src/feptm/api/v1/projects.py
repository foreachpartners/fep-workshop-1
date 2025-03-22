"""API endpoints for projects."""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional

from feptm.models import Project
from feptm.services.mock_data_service import mock_data_service

router = APIRouter()


@router.get("/", response_model=List[Project])
async def get_projects(
    status: Optional[str] = Query(None, description="Filter by status"),
    project_type: Optional[str] = Query(None, description="Filter by project type")
):
    """Get all projects with optional filtering.
    
    Args:
        status: Filter by project status
        project_type: Filter by project type
    
    Returns:
        List of projects
    """
    filters = {}
    if status is not None:
        filters["status"] = status
    if project_type is not None:
        filters["project_type"] = project_type
        
    projects = mock_data_service.get_filtered_data("projects", filters)
    return projects


@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: str = Path(..., description="The ID of the project to get")
):
    """Get a project by ID.
    
    Args:
        project_id: ID of the project
    
    Returns:
        Project if found
        
    Raises:
        HTTPException: If project not found
    """
    project = mock_data_service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found")
    return project 