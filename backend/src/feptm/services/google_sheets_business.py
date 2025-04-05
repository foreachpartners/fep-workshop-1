"""Business logic for working with Google Sheets."""

from datetime import datetime
from typing import Dict, Optional

from googleapiclient.errors import HttpError

from feptm.models import Project
from feptm.services.google_sheets_helper import get_sheet_by_name


def update_project_info_sheet(sheets_service, spreadsheet_id: str, project: Project) -> None:
    """Update project info sheet with metadata.
    
    Args:
        sheets_service: Google Sheets service instance
        spreadsheet_id: ID of the spreadsheet
        project: Project object
        
    Returns:
        None
    """
    try:
        # Get "Project info" sheet
        project_info_sheet = get_sheet_by_name(sheets_service, spreadsheet_id, "Project info")
        
        if not project_info_sheet:
            raise Exception(f"Failed to find sheet 'Project info' in the spreadsheet with ID {spreadsheet_id}")
        
        sheet_title = project_info_sheet['properties']['title']
        
        # Prepare data in "Name"/"Value" model
        project_data = [
            ["Name", "Value"],
            ["ProjectName", project.name or ""]
        ]
        
        # Add link to the project info document
        spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
        project_data.append(["Project Info", f'=HYPERLINK("{spreadsheet_url}"; "{spreadsheet_url}")'])
        
        # Add link to project folder if available
        if project.drive_folder_id:
            folder_url = f"https://drive.google.com/drive/folders/{project.drive_folder_id}"
            project_data.append(["Project Folder", f'=HYPERLINK("{folder_url}"; "{folder_url}")'])
        
        # Add links to created documents if they exist
        if project.calculations_spreadsheet_url:
            project_data.append(["Payment Distribution", f'=HYPERLINK("{project.calculations_spreadsheet_url}"; "{project.calculations_spreadsheet_url}")'])
        if project.report_spreadsheet_url:
            project_data.append(["General Expenses", f'=HYPERLINK("{project.report_spreadsheet_url}"; "{project.report_spreadsheet_url}")'])
        
        # First clear the range to remove old data
        try:
            sheets_service.spreadsheets().values().clear(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_title}!A1:B15",
                body={}
            ).execute()
        except HttpError as error:
            print(f"Warning: Failed to clear range before update: {error}")
        
        # Update the document sheet using exact sheet name
        request = sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_title}!A1:B15",  # Increased range for adding new fields
            valueInputOption="USER_ENTERED",
            body={"values": project_data}
        ).execute()
        
        return None
    except HttpError as error:
        raise Exception(f"Failed to update project info sheet: {error}")


def format_project_info_sheet(sheets_service, spreadsheet_id: str) -> None:
    """Format the project info sheet.
    
    Args:
        sheets_service: Google Sheets service instance
        spreadsheet_id: ID of the spreadsheet
        
    Returns:
        None
    """
    try:
        # Get "Project info" sheet
        project_info_sheet = get_sheet_by_name(sheets_service, spreadsheet_id, "Project info")
        
        if not project_info_sheet:
            raise Exception(f"Failed to find sheet 'Project info' in the spreadsheet with ID {spreadsheet_id}")
        
        sheet_id = project_info_sheet['properties']['sheetId']
        
        format_requests = [
            # Title formatting
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 0,
                        "endRowIndex": 1,
                        "startColumnIndex": 0,
                        "endColumnIndex": 8
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "textFormat": {
                                "fontSize": 14,
                                "bold": True
                            },
                            "backgroundColor": {
                                "red": 0.95,
                                "green": 0.95,
                                "blue": 0.95
                            }
                        }
                    },
                    "fields": "userEnteredFormat(textFormat,backgroundColor)"
                }
            },
            # Section headers formatting
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 5,
                        "endRowIndex": 6,
                        "startColumnIndex": 0,
                        "endColumnIndex": 8
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "textFormat": {
                                "bold": True
                            },
                            "backgroundColor": {
                                "red": 0.95,
                                "green": 0.95,
                                "blue": 0.95
                            }
                        }
                    },
                    "fields": "userEnteredFormat(textFormat,backgroundColor)"
                }
            },
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 10,
                        "endRowIndex": 11,
                        "startColumnIndex": 0,
                        "endColumnIndex": 8
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "textFormat": {
                                "bold": True
                            },
                            "backgroundColor": {
                                "red": 0.95,
                                "green": 0.95,
                                "blue": 0.95
                            }
                        }
                    },
                    "fields": "userEnteredFormat(textFormat,backgroundColor)"
                }
            },
            # Formatting for "Related documents" section
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 18,  # Approximate position for "Related documents" section
                        "endRowIndex": 19,
                        "startColumnIndex": 0,
                        "endColumnIndex": 8
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "textFormat": {
                                "bold": True
                            },
                            "backgroundColor": {
                                "red": 0.95,
                                "green": 0.95,
                                "blue": 0.95
                            }
                        }
                    },
                    "fields": "userEnteredFormat(textFormat,backgroundColor)"
                }
            },
            # Headers for related documents table
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 20,  # Column headers
                        "endRowIndex": 21,
                        "startColumnIndex": 0,
                        "endColumnIndex": 2
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "textFormat": {
                                "bold": True
                            },
                            "backgroundColor": {
                                "red": 0.95,
                                "green": 0.95,
                                "blue": 0.95
                            }
                        }
                    },
                    "fields": "userEnteredFormat(textFormat,backgroundColor)"
                }
            },
            # Field labels formatting
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 2,
                        "endRowIndex": 17,
                        "startColumnIndex": 0,
                        "endColumnIndex": 1
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "textFormat": {
                                "bold": True
                            }
                        }
                    },
                    "fields": "userEnteredFormat(textFormat)"
                }
            }
        ]
        
        # Execute the formatting requests
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": format_requests}
        ).execute()
        
        return None
    except HttpError as error:
        raise Exception(f"Failed to format project info sheet: {error}")


def create_project_metadata(google_sheets_service, project: Project) -> Dict[str, str]:
    """Create Google Sheets with project metadata and setup.
    
    Args:
        google_sheets_service: GoogleSheetsService instance
        project: Project object with at least the name
        
    Returns:
        Dictionary with spreadsheet ID and URL
    """
    # Create a new spreadsheet for the project
    spreadsheet_info = google_sheets_service.create_spreadsheet(project.name)
    
    # ID of the new spreadsheet
    spreadsheet_id = spreadsheet_info["spreadsheet_id"]
    
    # Get spreadsheet URL
    spreadsheet_url = spreadsheet_info["spreadsheet_url"]
    
    # Update project information
    update_project_info_sheet(google_sheets_service.sheets_service, spreadsheet_id, project)
    
    # Format the spreadsheet for better display
    format_project_info_sheet(google_sheets_service.sheets_service, spreadsheet_id)
    
    # If project has a folder ID, move the spreadsheet to this folder
    drive_folder_url = None
    if project.drive_folder_id:
        try:
            # Move spreadsheet to specified folder
            google_sheets_service.drive_service.files().update(
                fileId=spreadsheet_id,
                addParents=project.drive_folder_id,
                removeParents='root',
                fields='id, parents'
            ).execute()
            
            # Create folder URL
            drive_folder_url = f"https://drive.google.com/drive/folders/{project.drive_folder_id}"
        except HttpError as error:
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