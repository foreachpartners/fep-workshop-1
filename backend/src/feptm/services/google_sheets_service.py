"""Service for working with Google Sheets API."""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any

from google.oauth2.credentials import Credentials as UserCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from feptm.core.config import settings
from feptm.core.utils import generate_uuid
from feptm.models import ProjectMeta


class GoogleSheetsService:
    """Service for working with Google Sheets API."""

    def __init__(self):
        """Initialize service with credentials."""
        self.credentials_file = settings.GOOGLE_CREDENTIALS_FILE or self._find_credentials_file()
        self.token_file = settings.GOOGLE_TOKEN_FILE or os.path.expanduser("~/.google_sheets_token.json")
        self.sheets_service = None
        self.drive_service = None
        self.initialize()

    def _find_credentials_file(self) -> str:
        """Find the credentials file in default locations.
        
        Returns:
            Path to the credentials file
            
        Raises:
            FileNotFoundError: If no credentials file can be found
        """
        default_locations = [
            "credentials.json",
            "backend/credentials.json",
            os.path.expanduser("~/.config/google/credentials.json"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "credentials.json"),
        ]
        
        # Check default locations
        for location in default_locations:
            if os.path.isfile(location):
                return location
        
        # If we get here, no credentials file was found
        locations_str = "\n- ".join([""] + default_locations)
        raise FileNotFoundError(
            f"Could not find Google API credentials file. "
            f"Please place credentials.json in one of the following locations:{locations_str}"
        )

    def initialize(self) -> bool:
        """Initialize the Google Drive and Sheets API services.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Set up OAuth 2.0 credentials
            creds = self._get_credentials()
            if not creds:
                print("Failed to obtain OAuth credentials")
                return False
                
            # Build the services
            self.drive_service = build('drive', 'v3', credentials=creds)
            self.sheets_service = build('sheets', 'v4', credentials=creds)
            
            print("Google Drive and Sheets services initialized successfully")
            return True
            
        except Exception as e:
            print(f"Error initializing Google services: {str(e)}")
            self.drive_service = None
            self.sheets_service = None
            return False
    
    def _get_credentials(self) -> Optional[UserCredentials]:
        """Get OAuth credentials for Google API.
        
        Returns:
            OAuth credentials
        """
        creds = None
        scopes = [
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/spreadsheets'
        ]
        
        # Check if token file exists and load credentials from it
        if self.token_file and Path(self.token_file).exists():
            try:
                creds = UserCredentials.from_authorized_user_info(
                    json.loads(Path(self.token_file).read_text()),
                    scopes
                )
            except Exception as e:
                print(f"Error loading token file: {str(e)}")
        
        # If there are no valid credentials, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # Load client secrets from the credentials file
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, scopes)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            if self.token_file:
                token_path = Path(self.token_file)
                token_path.parent.mkdir(parents=True, exist_ok=True)
                token_path.write_text(json.dumps({
                    'token': creds.token,
                    'refresh_token': creds.refresh_token,
                    'token_uri': creds.token_uri,
                    'client_id': creds.client_id,
                    'client_secret': creds.client_secret,
                    'scopes': creds.scopes
                }))
                print(f"Saved credentials to {self.token_file}")
        
        return creds

    def create_spreadsheet(self, title: str) -> Dict[str, str]:
        """Create a new Google Sheets spreadsheet.
        
        Args:
            title: Title of the spreadsheet
            
        Returns:
            Dictionary with spreadsheet ID and URL
        """
        spreadsheet_body = {
            "properties": {
                "title": title
            },
            "sheets": [
                {
                    "properties": {
                        "title": "Информация о проекте",
                        "gridProperties": {
                            "rowCount": 20,
                            "columnCount": 8
                        }
                    }
                },
                {
                    "properties": {
                        "title": "Специалисты проекта",
                        "gridProperties": {
                            "rowCount": 100,
                            "columnCount": 8
                        }
                    }
                },
                {
                    "properties": {
                        "title": "Периоды оплаты",
                        "gridProperties": {
                            "rowCount": 100,
                            "columnCount": 6
                        }
                    }
                }
            ]
        }
        
        try:
            spreadsheet = self.sheets_service.spreadsheets().create(
                body=spreadsheet_body
            ).execute()
            
            spreadsheet_id = spreadsheet.get("spreadsheetId")
            spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
            
            return {
                "spreadsheet_id": spreadsheet_id,
                "spreadsheet_url": spreadsheet_url
            }
        except HttpError as error:
            raise Exception(f"Failed to create spreadsheet: {error}")

    def _get_sheet_ids(self, spreadsheet_id: str) -> Dict[str, int]:
        """Get sheet IDs for the given spreadsheet.
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            
        Returns:
            Dictionary with sheet titles as keys and sheet IDs as values
        """
        try:
            # Get spreadsheet metadata
            spreadsheet_metadata = self.sheets_service.spreadsheets().get(
                spreadsheetId=spreadsheet_id
            ).execute()
            
            # Extract sheet IDs
            sheet_ids = {}
            for sheet in spreadsheet_metadata.get('sheets', []):
                title = sheet.get('properties', {}).get('title')
                sheet_id = sheet.get('properties', {}).get('sheetId')
                sheet_ids[title] = sheet_id
            
            return sheet_ids
        except HttpError as error:
            raise Exception(f"Failed to get sheet IDs: {error}")

    def update_project_info_sheet(
        self, spreadsheet_id: str, project_meta: ProjectMeta
    ) -> None:
        """Update project info sheet with metadata.
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            project_meta: Project metadata
            
        Returns:
            None
        """
        # Prepare project info data
        project_data = [
            ["Информация о проекте", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["Название проекта", project_meta.name or "", "", "", "", "", "", ""],
            ["Описание", project_meta.description or "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["Информация о заказчике", "", "", "", "", "", "", ""],
            ["Название компании", project_meta.client_name or "", "", "", "", "", "", ""],
            ["Email", project_meta.client_contact_email or "", "", "", "", "", "", ""],
            ["Телефон", project_meta.client_contact_phone or "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["Информация о проекте", "", "", "", "", "", "", ""],
            ["Дата начала", project_meta.start_date.isoformat() if project_meta.start_date else "", "", "", "", "", "", ""],
            ["Дата окончания", project_meta.end_date.isoformat() if project_meta.end_date else "", "", "", "", "", "", ""],
            ["Тип проекта", project_meta.project_type.value if project_meta.project_type else "", "", "", "", "", "", ""],
            ["Бюджет", str(project_meta.budget) if project_meta.budget else "", "", "", "", "", "", ""],
            ["Номер договора", project_meta.contract_number or "", "", "", "", "", "", ""],
            ["ID папки на Google Drive", project_meta.drive_folder_id or "", "", "", "", "", "", ""],
        ]
        
        try:
            # Update the "Информация о проекте" sheet
            request = self.sheets_service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range="Информация о проекте!A1:H17",
                valueInputOption="USER_ENTERED",
                body={"values": project_data}
            ).execute()
            
            # Format the sheet
            self._format_project_info_sheet(spreadsheet_id)
            
            return None
        except HttpError as error:
            raise Exception(f"Failed to update project info sheet: {error}")
    
    def update_specialists_sheet(self, spreadsheet_id: str) -> None:
        """Set up the specialists sheet headers.
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            
        Returns:
            None
        """
        # Prepare specialists header data
        specialists_headers = [
            ["ID", "ФИО", "Роль", "Email", "Ставка в час", "Дата начала", "Дата окончания", "Статус"]
        ]
        
        try:
            # Update the "Специалисты проекта" sheet
            request = self.sheets_service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range="Специалисты проекта!A1:H1",
                valueInputOption="USER_ENTERED",
                body={"values": specialists_headers}
            ).execute()
            
            # Format the sheet
            self._format_specialists_sheet(spreadsheet_id)
            
            return None
        except HttpError as error:
            raise Exception(f"Failed to update specialists sheet: {error}")
    
    def update_periods_sheet(self, spreadsheet_id: str) -> None:
        """Set up the payment periods sheet headers.
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            
        Returns:
            None
        """
        # Prepare payment periods header data
        periods_headers = [
            ["ID", "Название периода", "Дата начала", "Дата окончания", "Статус", "Ссылка на отчет"]
        ]
        
        try:
            # Update the "Периоды оплаты" sheet
            request = self.sheets_service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range="Периоды оплаты!A1:F1",
                valueInputOption="USER_ENTERED",
                body={"values": periods_headers}
            ).execute()
            
            # Format the sheet
            self._format_periods_sheet(spreadsheet_id)
            
            return None
        except HttpError as error:
            raise Exception(f"Failed to update periods sheet: {error}")
    
    def _format_project_info_sheet(self, spreadsheet_id: str) -> None:
        """Format the project info sheet.
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            
        Returns:
            None
        """
        try:
            # Get sheet IDs
            sheet_ids = self._get_sheet_ids(spreadsheet_id)
            sheet_id = sheet_ids.get("Информация о проекте")
            
            if not sheet_id:
                print("Warning: Could not find sheet ID for 'Информация о проекте'. Formatting will be skipped.")
                return None
                
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
            self.sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={"requests": format_requests}
            ).execute()
            
            return None
        except HttpError as error:
            raise Exception(f"Failed to format project info sheet: {error}")
    
    def _format_specialists_sheet(self, spreadsheet_id: str) -> None:
        """Format the specialists sheet.
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            
        Returns:
            None
        """
        try:
            # Get sheet IDs
            sheet_ids = self._get_sheet_ids(spreadsheet_id)
            sheet_id = sheet_ids.get("Специалисты проекта")
            
            if not sheet_id:
                print("Warning: Could not find sheet ID for 'Специалисты проекта'. Formatting will be skipped.")
                return None
                
            format_requests = [
                # Headers formatting
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
                }
            ]
            
            # Execute the formatting requests
            self.sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={"requests": format_requests}
            ).execute()
            
            return None
        except HttpError as error:
            raise Exception(f"Failed to format specialists sheet: {error}")
    
    def _format_periods_sheet(self, spreadsheet_id: str) -> None:
        """Format the payment periods sheet.
        
        Args:
            spreadsheet_id: ID of the spreadsheet
            
        Returns:
            None
        """
        try:
            # Get sheet IDs
            sheet_ids = self._get_sheet_ids(spreadsheet_id)
            sheet_id = sheet_ids.get("Периоды оплаты")
            
            if not sheet_id:
                print("Warning: Could not find sheet ID for 'Периоды оплаты'. Formatting will be skipped.")
                return None
                
            format_requests = [
                # Headers formatting
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": 0,
                            "endRowIndex": 1,
                            "startColumnIndex": 0,
                            "endColumnIndex": 6
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
                }
            ]
            
            # Execute the formatting requests
            self.sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={"requests": format_requests}
            ).execute()
            
            return None
        except HttpError as error:
            raise Exception(f"Failed to format periods sheet: {error}")
    
    def create_project_metadata(self, project_meta: ProjectMeta) -> Dict[str, str]:
        """Create a Google Sheets document with project metadata.
        
        Args:
            project_meta: Project metadata
            
        Returns:
            Dictionary with spreadsheet ID, URL, and project ID
        """
        # Generate a unique ID for the project
        project_id = generate_uuid()
        
        # Create a new spreadsheet
        spreadsheet_info = self.create_spreadsheet(f"Проект: {project_meta.name}")
        
        # Update project info sheet
        self.update_project_info_sheet(spreadsheet_info["spreadsheet_id"], project_meta)
        
        # Set up specialists sheet
        self.update_specialists_sheet(spreadsheet_info["spreadsheet_id"])
        
        # Set up payment periods sheet
        self.update_periods_sheet(spreadsheet_info["spreadsheet_id"])
        
        # If a drive folder ID is provided, move the spreadsheet to that folder
        drive_folder_url = None
        if project_meta.drive_folder_id:
            try:
                # Move the spreadsheet to the specified folder
                self.drive_service.files().update(
                    fileId=spreadsheet_info["spreadsheet_id"],
                    addParents=project_meta.drive_folder_id,
                    removeParents="root",
                    fields="id, parents"
                ).execute()
                
                drive_folder_url = f"https://drive.google.com/drive/folders/{project_meta.drive_folder_id}"
            except HttpError as error:
                # Log the error but continue (non-critical)
                print(f"Failed to move spreadsheet to folder: {error}")
        
        return {
            "project_id": project_id,
            "spreadsheet_id": spreadsheet_info["spreadsheet_id"],
            "spreadsheet_url": spreadsheet_info["spreadsheet_url"],
            "drive_folder_id": project_meta.drive_folder_id,
            "drive_folder_url": drive_folder_url
        }
    
    def create_drive_folder(self, folder_name: str, parent_folder_id: Optional[str] = None) -> Dict[str, str]:
        """Create a folder in Google Drive.
        
        Args:
            folder_name: Name of the folder
            parent_folder_id: ID of the parent folder (optional)
            
        Returns:
            Dictionary with folder ID and URL
        """
        # Prepare folder metadata
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        # If parent folder ID is provided, set it as parent
        if parent_folder_id:
            folder_metadata['parents'] = [parent_folder_id]
        
        # Create the folder
        try:
            folder = self.drive_service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            
            folder_id = folder.get('id')
            folder_url = f"https://drive.google.com/drive/folders/{folder_id}"
            
            return {
                "folder_id": folder_id,
                "folder_url": folder_url
            }
        except HttpError as error:
            raise Exception(f"Failed to create folder: {error}")
    
    def copy_spreadsheet_from_template(self, template_id: str, new_title: str, folder_id: str) -> Dict[str, str]:
        """Copy a spreadsheet from a template and move it to a folder.
        
        Args:
            template_id: ID of the template spreadsheet
            new_title: Title for the new spreadsheet
            folder_id: ID of the folder where to place the copy
            
        Returns:
            Dictionary with spreadsheet ID and URL
        """
        try:
            # Copy the spreadsheet
            copied_file = self.drive_service.files().copy(
                fileId=template_id,
                body={'name': new_title},
                fields='id'
            ).execute()
            
            spreadsheet_id = copied_file.get('id')
            
            # Move the spreadsheet to the specified folder
            self.drive_service.files().update(
                fileId=spreadsheet_id,
                addParents=folder_id,
                removeParents='root',
                fields='id, parents'
            ).execute()
            
            spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
            
            return {
                "spreadsheet_id": spreadsheet_id,
                "spreadsheet_url": spreadsheet_url
            }
        except HttpError as error:
            if error.resp.status == 404:
                raise Exception(f"Failed to copy spreadsheet: Template with ID {template_id} not found. Make sure the file exists and you have access to it.")
            else:
                raise Exception(f"Failed to copy spreadsheet: {error}")
        except Exception as e:
            raise Exception(f"Failed to copy spreadsheet: {e}")
    
    def create_project(self, project_meta: ProjectMeta) -> Dict[str, str]:
        """Create a project in Google Drive with all required components.
        
        Args:
            project_meta: Project metadata with at least the name
            
        Returns:
            Dictionary with project details including IDs and URLs
        """
        if not self.is_initialized():
            raise Exception("Google services are not initialized. Please check your credentials and scopes.")
            
        try:
            # Generate a unique ID for the project
            project_id = generate_uuid()
            project_name = project_meta.name
            
            # 1. Create a folder for the project
            parent_folder_id = settings.GOOGLE_PROJECTS_FOLDER_ID
            
            # Create folder in root or parent folder
            if parent_folder_id:
                # Verify that parent folder exists and is accessible
                try:
                    self.drive_service.files().get(fileId=parent_folder_id, fields="id,name").execute()
                except HttpError as error:
                    if error.resp.status == 404:
                        raise Exception(f"Parent folder with ID {parent_folder_id} not found. Check GOOGLE_PROJECTS_FOLDER_ID setting and make sure you have access to this folder.")
                    else:
                        raise Exception(f"Error accessing parent folder: {str(error)}")
                
                folder_info = self.create_drive_folder(f"Проект: {project_name}", parent_folder_id)
            else:
                # If no parent folder ID is set, create in the root of Google Drive
                folder_info = self.create_drive_folder(f"Проект: {project_name}")
                
            project_folder_id = folder_info["folder_id"]
            
            # 2. Create project info spreadsheet from template
            project_info_template_id = settings.GOOGLE_PROJECT_INFO_TEMPLATE_ID
            if not project_info_template_id:
                raise Exception("GOOGLE_PROJECT_INFO_TEMPLATE_ID is not configured in settings")
            
            # Verify that template exists and is accessible
            try:
                self.drive_service.files().get(fileId=project_info_template_id, fields="id,name").execute()
            except HttpError as error:
                if error.resp.status == 404:
                    raise Exception(f"Project info template with ID {project_info_template_id} not found. Check GOOGLE_PROJECT_INFO_TEMPLATE_ID setting and make sure you have access to this file.")
                else:
                    raise Exception(f"Error accessing project info template: {str(error)}")
            
            project_info = self.copy_spreadsheet_from_template(
                project_info_template_id,
                f"{project_name} - Информация о проекте",
                project_folder_id
            )
            
            # 3. Create report spreadsheet from template
            report_template_id = settings.GOOGLE_PROJECT_REPORT_TEMPLATE_ID
            if not report_template_id:
                raise Exception("GOOGLE_PROJECT_REPORT_TEMPLATE_ID is not configured in settings")
            
            # Verify that template exists and is accessible
            try:
                self.drive_service.files().get(fileId=report_template_id, fields="id,name").execute()
            except HttpError as error:
                if error.resp.status == 404:
                    raise Exception(f"Report template with ID {report_template_id} not found. Check GOOGLE_PROJECT_REPORT_TEMPLATE_ID setting and make sure you have access to this file.")
                else:
                    raise Exception(f"Error accessing report template: {str(error)}")
            
            report = self.copy_spreadsheet_from_template(
                report_template_id,
                f"{project_name} - Сводный отчет",
                project_folder_id
            )
            
            # 4. Create calculations spreadsheet from template
            calculations_template_id = settings.GOOGLE_PROJECT_CALCULATIONS_TEMPLATE_ID
            if not calculations_template_id:
                raise Exception("GOOGLE_PROJECT_CALCULATIONS_TEMPLATE_ID is not configured in settings")
            
            # Verify that template exists and is accessible
            try:
                self.drive_service.files().get(fileId=calculations_template_id, fields="id,name").execute()
            except HttpError as error:
                if error.resp.status == 404:
                    raise Exception(f"Calculations template with ID {calculations_template_id} not found. Check GOOGLE_PROJECT_CALCULATIONS_TEMPLATE_ID setting and make sure you have access to this file.")
                else:
                    raise Exception(f"Error accessing calculations template: {str(error)}")
            
            calculations = self.copy_spreadsheet_from_template(
                calculations_template_id,
                f"{project_name} - Расчеты",
                project_folder_id
            )
            
            # Return all information about the created project
            return {
                "project_id": project_id,
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
                    self.drive_service.files().delete(fileId=project_folder_id).execute()
                    print(f"Cleaned up folder {project_folder_id} after error")
            except Exception as cleanup_error:
                print(f"Failed to clean up resources after error: {str(cleanup_error)}")
            
            raise Exception(f"Failed to create project: {str(e)}")

    def is_initialized(self) -> bool:
        """Check if the service is properly initialized.
        
        Returns:
            True if both drive and sheets services are initialized, False otherwise
        """
        return self.drive_service is not None and self.sheets_service is not None


# Create singleton instance
google_sheets_service = GoogleSheetsService() 