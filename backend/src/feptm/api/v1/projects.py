"""API endpoints for projects."""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from feptm.models import Project, ProjectMetaResponse
from feptm.services.google_sheets_service import google_sheets_service
from feptm.timesheets.project_service import TimesheetProjectService
from feptm.core.config import settings

router = APIRouter()


@router.get("/", response_model=List[Project])
async def get_projects():
    """Get all projects.
    
    Returns:
        List of projects
    """
    # Note: This is a stub that needs to be implemented with real data
    # TODO: Implement actual project retrieval from database
    return []


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
    # Note: This is a stub that needs to be implemented with real data
    # TODO: Implement actual project retrieval from database
    raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found")


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
        # Validate configuration
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
        
        # Create minimal Project with just the name
        project = Project(name=request.project_name)
        
        # Initialize timesheet project service with the Google Sheets service
        timesheet_service = TimesheetProjectService(google_sheets_service)
        
        # Create project in Google Drive
        result = timesheet_service.create_project(project)
        
        # Return the response
        return ProjectMetaResponse(
            project_id=result["project_id"],
            created=project.created,
            modified=project.modified,
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