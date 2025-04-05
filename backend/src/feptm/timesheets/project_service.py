"""Business logic for project management in timesheets."""

from datetime import datetime
from typing import Dict, List, Optional, Any

from feptm.core.config import settings
from feptm.models import Project
from feptm.services.google_sheets_service import GoogleSheetsService


class TimesheetProjectService:
    """Service for managing projects in timesheets."""

    def __init__(self, google_sheets_service: GoogleSheetsService):
        """Initialize the service with Google Sheets service.
        
        Args:
            google_sheets_service: Google Sheets service instance
        """
        self.google_sheets_service = google_sheets_service
    
    def update_project_info_sheet(self, spreadsheet_id: str, project: Project) -> None:
        """Update project info sheet with metadata.
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            project: Project object
            
        Returns:
            None
        """
        try:
            # Prepare project data structure
            project_data = [
                ["Name", "Value"],  # Headers
                ["ProjectName", project.name or ""]
            ]
            
            # Add link to the project info document
            spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
            project_data.append(["Project Info", f'=HYPERLINK("{spreadsheet_url}"; "{spreadsheet_url}")'])
            
            # Add link to project folder if available
            folder_url = project.drive_folder_url
            project_data.append(["Project Folder", f'=HYPERLINK("{folder_url}"; "{folder_url}")'])
            
            # Add links to created documents
            project_data.append(["Payment Distribution", f'=HYPERLINK("{project.calculations_spreadsheet_url}"; "{project.calculations_spreadsheet_url}")'])
            project_data.append(["General Expenses", f'=HYPERLINK("{project.report_spreadsheet_url}"; "{project.report_spreadsheet_url}")'])
            
            # Use the service to update the sheet
            self.google_sheets_service.update_project_sheet(
                spreadsheet_id=spreadsheet_id,
                sheet_name="Project info",
                data=project_data
            )
            
            return None
        except Exception as error:
            raise Exception(f"Failed to update project info sheet: {error}")

    def format_project_info_sheet(self, spreadsheet_id: str) -> None:
        """Format the project info sheet.
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            
        Returns:
            None
        """
        try:
            # Let the service handle sheet formatting with default settings
            self.google_sheets_service.format_project_sheet(
                spreadsheet_id=spreadsheet_id,
                sheet_name="Project info"
            )
            
            return None
        except Exception as error:
            raise Exception(f"Failed to format project info sheet: {error}")
    
    def _create_spreadsheet_from_template(self, template_id: str, new_title: str, folder_id: str) -> Dict[str, str]:
        """Helper method to create a spreadsheet from a template.
        
        Args:
            template_id: ID of the template spreadsheet
            new_title: Title for the new spreadsheet
            folder_id: ID of the folder where to place the copy
            
        Returns:
            Dictionary with spreadsheet ID and URL
            
        Raises:
            Exception: If template ID is not configured or accessible
        """
        if not template_id:
            raise Exception(f"Template ID is not configured in settings")
        
        # Create spreadsheet from template
        result = self.google_sheets_service.ensure_spreadsheet_from_template(
            template_id=template_id,
            new_title=new_title,
            folder_id=folder_id
        )
        
        print(f"Created spreadsheet: {new_title} (ID: {result.get('spreadsheet_id')})")
        return result

    def create_project(self, project: Project) -> Dict[str, str]:
        """Create a project in Google Drive with all required components.
        
        Args:
            project: Project object with at least the name
            
        Returns:
            Dictionary with project details including IDs and URLs
        """
        if not self.google_sheets_service.is_initialized():
            raise Exception("Google services are not initialized. Please check your credentials and scopes.")
            
        try:
            project_name = project.name
            
            print(f"Creating project: {project_name}")
            
            # 1. Create a folder for the project
            parent_folder_id = settings.GOOGLE_PROJECTS_FOLDER_ID
            
            # Create folder in root or parent folder
            if parent_folder_id:
                # Verify that parent folder exists and is accessible
                try:
                    parent_folder = self.google_sheets_service.get_file(parent_folder_id)
                    print(f"Parent folder found: {parent_folder.get('name')} (ID: {parent_folder.get('id')})")
                except Exception as error:
                    raise Exception(f"Parent folder with ID {parent_folder_id} not found or not accessible: {str(error)}")
                
                folder_info = self.google_sheets_service.create_drive_folder(f"{project_name}", parent_folder_id)
            else:
                # If no parent folder ID is set, create in the root of Google Drive
                folder_info = self.google_sheets_service.create_drive_folder(f"{project_name}")
                
            project_folder_id = folder_info["folder_id"]
            print(f"Created project folder: {project_name} (ID: {project_folder_id})")
            
            # 2. Create project info spreadsheet from template
            project_info = self._create_spreadsheet_from_template(
                template_id=settings.GOOGLE_PROJECT_INFO_TEMPLATE_ID,
                new_title=f"{project_name} - Project info",
                folder_id=project_folder_id
            )
            
            # 3. Create report spreadsheet from template
            report = self._create_spreadsheet_from_template(
                template_id=settings.GOOGLE_PROJECT_REPORT_TEMPLATE_ID,
                new_title=f"{project_name} - General Expenses",
                folder_id=project_folder_id
            )
            
            # 4. Create calculations spreadsheet from template
            calculations = self._create_spreadsheet_from_template(
                template_id=settings.GOOGLE_PROJECT_CALCULATIONS_TEMPLATE_ID,
                new_title=f"{project_name} - Payment Distribution",
                folder_id=project_folder_id
            )
            
            # Update project with information about created resources
            project.drive_folder_id = project_folder_id
            project.project_info_spreadsheet_id = project_info["spreadsheet_id"]
            project.report_spreadsheet_id = report["spreadsheet_id"]
            project.calculations_spreadsheet_id = calculations["spreadsheet_id"]
            project.modified = datetime.utcnow()
            
            # Update main project information
            print(f"Updating project info with links to related documents:")
            print(f"  - Project name: {project_name}")
            print(f"  - Project info URL: {project_info['spreadsheet_url']}")
            print(f"  - Folder URL: https://drive.google.com/drive/folders/{project_folder_id}")
            print(f"  - Calculations URL: {calculations['spreadsheet_url']}")
            print(f"  - Report URL: {report['spreadsheet_url']}")
            
            self.update_project_info_sheet(project_info["spreadsheet_id"], project)
            print(f"Project info updated successfully")
            
            # Return all information about the created project
            return {
                "project_id": project.id,
                "drive_folder_id": project_folder_id,
                "drive_folder_url": folder_info["folder_url"],
                "project_info_spreadsheet_id": project_info["spreadsheet_id"],
                "project_info_spreadsheet_url": project_info["spreadsheet_url"],
                "report_spreadsheet_id": report["spreadsheet_id"],
                "report_spreadsheet_url": report["spreadsheet_url"],
                "calculations_spreadsheet_id": calculations["spreadsheet_id"],
                "calculations_spreadsheet_url": calculations["spreadsheet_url"]
            }
        except Exception as e:
            # Clean up any created resources on failure
            try:
                if 'project_folder_id' in locals():
                    self.google_sheets_service.delete_file(project_folder_id)
                    print(f"Cleaned up folder {project_folder_id} after error")
            except Exception as cleanup_error:
                print(f"Failed to clean up resources after error: {str(cleanup_error)}")
            
            raise Exception(f"Failed to create project: {str(e)}")

    def create_project_metadata(self, project: Project) -> Dict[str, str]:
        """Create Google Sheets with project metadata and setup.
        
        Args:
            project: Project object with at least the name
            
        Returns:
            Dictionary with spreadsheet ID and URL
        """
        # Create a new spreadsheet for the project
        spreadsheet_info = self.google_sheets_service.create_spreadsheet(project.name)
        
        # ID of the new spreadsheet
        spreadsheet_id = spreadsheet_info["spreadsheet_id"]
        
        # Get spreadsheet URL
        spreadsheet_url = spreadsheet_info["spreadsheet_url"]
        
        # Update project information
        self.update_project_info_sheet(spreadsheet_id, project)
        
        # Format the spreadsheet for better display
        self.format_project_info_sheet(spreadsheet_id)
        
        # If project has a folder ID, move the spreadsheet to this folder
        drive_folder_url = None
        if project.drive_folder_id:
            try:
                # Move spreadsheet to specified folder
                self.google_sheets_service.move_file(
                    file_id=spreadsheet_id,
                    folder_id=project.drive_folder_id
                )
                
                # Create folder URL
                drive_folder_url = f"https://drive.google.com/drive/folders/{project.drive_folder_id}"
            except Exception as error:
                print(f"Failed to move spreadsheet to folder: {error}")
        
        # Generate a unique ID for the project if it doesn't have one
        project_id = project.id
        
        return {
            "project_id": project_id,
            "spreadsheet_id": spreadsheet_info["spreadsheet_id"],
            "spreadsheet_url": spreadsheet_info["spreadsheet_url"],
            "drive_folder_id": project.drive_folder_id,
            "drive_folder_url": drive_folder_url
        } 