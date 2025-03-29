"""API endpoints for projects."""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional
from pydantic import BaseModel

from feptm.models import Project, ProjectMeta, ProjectMetaResponse
from feptm.services.mock_data_service import mock_data_service
from feptm.services.google_sheets_service import google_sheets_service
from feptm.core.config import settings

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


class ProjectCreateRequest(BaseModel):
    """Request model for creating a project."""
    project_name: str


@router.post("/create", response_model=ProjectMetaResponse)
async def create_project(request: ProjectCreateRequest):
    """Create a new project in Google Drive.
    
    This endpoint creates:
    1. A folder in Google Drive with the project name
    2. A Google Sheet with project info based on the template
    3. A report file linked to the project info
    4. A calculations sheet for the project
    
    Args:
        request: Project creation request containing project name
        
    Returns:
        Project creation response with IDs and URLs
        
    Raises:
        HTTPException: If creation fails
    """
    try:
        # Validate configuration - проверяем наличие необходимых настроек
        # GOOGLE_PROJECTS_FOLDER_ID больше не обязательный параметр
        # if not settings.GOOGLE_PROJECTS_FOLDER_ID:
        #    raise HTTPException(
        #        status_code=500, 
        #        detail="GOOGLE_PROJECTS_FOLDER_ID not configured. Please set this value in the environment variables."
        #    )
        
        if not settings.GOOGLE_PROJECT_INFO_TEMPLATE_ID:
            raise HTTPException(
                status_code=500, 
                detail="GOOGLE_PROJECT_INFO_TEMPLATE_ID not configured. Please set this value in the environment variables."
            )
            
        if not settings.GOOGLE_PROJECT_REPORT_TEMPLATE_ID:
            raise HTTPException(
                status_code=500, 
                detail="GOOGLE_PROJECT_REPORT_TEMPLATE_ID not configured. Please set this value in the environment variables."
            )
            
        if not settings.GOOGLE_PROJECT_CALCULATIONS_TEMPLATE_ID:
            raise HTTPException(
                status_code=500, 
                detail="GOOGLE_PROJECT_CALCULATIONS_TEMPLATE_ID not configured. Please set this value in the environment variables."
            )
        
        # Create minimal ProjectMeta with just the name
        project_meta = ProjectMeta(name=request.project_name)
        
        # Create project in Google Drive
        result = google_sheets_service.create_project(project_meta)
        
        # Return the response
        return ProjectMetaResponse(
            project_id=result["project_id"],
            spreadsheet_id=result.get("spreadsheet_id", ""),
            spreadsheet_url=result.get("spreadsheet_url", ""),
            drive_folder_id=result.get("drive_folder_id", ""),
            drive_folder_url=result.get("drive_folder_url", ""),
            project_info_spreadsheet_id=result.get("project_info_spreadsheet_id", ""),
            project_info_spreadsheet_url=result.get("project_info_spreadsheet_url", ""),
            report_spreadsheet_id=result.get("report_spreadsheet_id", ""),
            report_spreadsheet_url=result.get("report_spreadsheet_url", ""),
            calculations_spreadsheet_id=result.get("calculations_spreadsheet_id", ""),
            calculations_spreadsheet_url=result.get("calculations_spreadsheet_url", "")
        )
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}") 