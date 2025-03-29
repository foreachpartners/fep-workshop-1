"""API endpoints for projects."""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional

from feptm.models import Project, ProjectMeta, ProjectMetaResponse
from feptm.services.mock_data_service import mock_data_service
from feptm.services.google_sheets_service import google_sheets_service

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


@router.post("/create", response_model=ProjectMetaResponse)
async def create_project_metadata(project_meta: ProjectMeta):
    """Create a new project metadata file in Google Sheets.
    
    This endpoint creates a new Google Sheets document with three sheets:
    1. "Информация о проекте" - contains general project information and client details
    2. "Специалисты проекта" - contains a table for project specialists
    3. "Периоды оплаты" - contains a table for payment periods
    
    Args:
        project_meta: Project metadata
        
    Returns:
        Project metadata creation response with IDs and URLs
        
    Raises:
        HTTPException: If creation fails
    """
    try:
        # Create project metadata in Google Sheets
        result = google_sheets_service.create_project_metadata(project_meta)
        
        # Return the response
        return ProjectMetaResponse(
            project_id=result["project_id"],
            spreadsheet_id=result["spreadsheet_id"],
            spreadsheet_url=result["spreadsheet_url"],
            drive_folder_id=result.get("drive_folder_id"),
            drive_folder_url=result.get("drive_folder_url")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create project metadata: {str(e)}") 