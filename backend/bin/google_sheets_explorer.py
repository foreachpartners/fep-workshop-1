#!/usr/bin/env python
import argparse
import datetime
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from google.oauth2.credentials import Credentials as UserCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("google_sheets_explorer")


# Define default credentials locations to check
DEFAULT_CREDENTIALS_LOCATIONS = [
    "credentials.json",
    "backend/credentials.json",
    os.path.expanduser("~/.config/google/credentials.json"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "credentials.json"),
]

# Define default token locations
DEFAULT_TOKEN_FILE = os.path.expanduser("~/.google_sheets_token.json")


class GoogleSheetsExplorer:
    """Tool for exploring and working with Google Sheets"""
    
    def __init__(self, credentials_file: Optional[str] = None, token_file: Optional[str] = None):
        """
        Initialize the Google Sheets explorer
        
        Args:
            credentials_file: Path to the Google API credentials file.
                              If None, will search in default locations.
            token_file: Path to the token file for storing OAuth tokens
        """
        self.logger = logging.getLogger(__name__)
        self.credentials_file = self._find_credentials_file(credentials_file)
        self.token_file = token_file or DEFAULT_TOKEN_FILE
        self.drive_service = None
        self.sheets_service = None
        
        self.logger.info(f"GoogleSheetsExplorer initialized with credentials file: {self.credentials_file}")
        self.logger.info(f"Token file: {self.token_file}")
        
    def _find_credentials_file(self, credentials_file: Optional[str] = None) -> str:
        """
        Find the credentials file in default locations if not explicitly provided
        
        Args:
            credentials_file: Explicitly provided credentials file path
            
        Returns:
            Path to the credentials file
            
        Raises:
            FileNotFoundError: If no credentials file can be found
        """
        # If credentials file is explicitly provided, check if it exists
        if credentials_file:
            if os.path.isfile(credentials_file):
                return credentials_file
            else:
                self.logger.warning(f"Provided credentials file not found: {credentials_file}")
                self.logger.info("Searching in default locations...")
        
        # Check default locations
        for location in DEFAULT_CREDENTIALS_LOCATIONS:
            if os.path.isfile(location):
                self.logger.info(f"Found credentials file at: {location}")
                return location
        
        # If we get here, no credentials file was found
        locations_str = "\n- ".join([""] + DEFAULT_CREDENTIALS_LOCATIONS)
        raise FileNotFoundError(
            f"Could not find Google API credentials file. "
            f"Please place credentials.json in one of the following locations:{locations_str}"
            f"\nor specify the path using --credentials"
        )
        
    def initialize(self) -> bool:
        """Initialize the Google Drive and Sheets API services"""
        try:
            # Set up OAuth 2.0 credentials
            credentials = self._get_credentials()
            if not credentials:
                self.logger.error("Failed to obtain OAuth credentials")
                return False
                
            # Build the services
            self.drive_service = build('drive', 'v3', credentials=credentials)
            self.sheets_service = build('sheets', 'v4', credentials=credentials)
            
            self.logger.info("Google Drive and Sheets services initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing Google services: {str(e)}")
            return False
    
    def _get_credentials(self) -> Optional[UserCredentials]:
        """
        Get OAuth credentials for Google API
        
        Returns:
            OAuth credentials
        """
        creds = None
        scopes = [
            'https://www.googleapis.com/auth/drive.readonly',
            'https://www.googleapis.com/auth/drive.file',
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
                self.logger.warning(f"Error loading token file: {str(e)}")
        
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
                self.logger.info(f"Saved credentials to {self.token_file}")
        
        return creds
    
    def list_files(self, folder_id: str) -> List[Dict[str, Any]]:
        """
        List all Google Sheets files in the specified folder
        
        Args:
            folder_id: ID of the Google Drive folder
            
        Returns:
            List of files with id, name, and lastModified info
        """
        if not self.drive_service:
            if not self.initialize():
                self.logger.error("Failed to initialize Google services")
                return []
                
        try:
            # Query for Google Sheets files in the specified folder
            query = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.spreadsheet'"
            
            # Execute the query
            results = self.drive_service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, createdTime, modifiedTime)',
                orderBy='modifiedTime desc'
            ).execute()
            
            files = results.get('files', [])
            
            self.logger.info(f"Found {len(files)} Google Sheets files in folder {folder_id}")
            return files
            
        except Exception as e:
            self.logger.error(f"Error listing files: {str(e)}")
            return []
    
    def create_test_spreadsheet(self, folder_id: str, name: Optional[str] = None) -> Optional[str]:
        """
        Create a test Google Sheets file in the specified folder
        
        Args:
            folder_id: ID of the Google Drive folder
            name: Name of the spreadsheet (defaults to "Test Sheet {timestamp}")
            
        Returns:
            ID of the created spreadsheet or None if failed
        """
        if not self.drive_service or not self.sheets_service:
            if not self.initialize():
                self.logger.error("Failed to initialize Google services")
                return None
                
        try:
            # Create a timestamp for unique name
            timestamp = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')
            
            # Use provided name or default with timestamp
            spreadsheet_name = name or f"Test Sheet {timestamp}"
            
            # Create a new spreadsheet
            spreadsheet = {
                'properties': {
                    'title': spreadsheet_name
                },
                'sheets': [
                    {
                        'properties': {
                            'title': 'Sample Data'
                        }
                    }
                ]
            }
            
            # Create the spreadsheet
            spreadsheet = self.sheets_service.spreadsheets().create(body=spreadsheet).execute()
            spreadsheet_id = spreadsheet.get('spreadsheetId')
            
            # Move the file to the specified folder
            if folder_id:
                # Get the current parents
                file = self.drive_service.files().get(
                    fileId=spreadsheet_id,
                    fields='parents'
                ).execute()
                previous_parents = ",".join(file.get('parents', []))
                
                # Move the file to the new folder
                self.drive_service.files().update(
                    fileId=spreadsheet_id,
                    addParents=folder_id,
                    removeParents=previous_parents,
                    fields='id, parents'
                ).execute()
            
            # Add sample data to the spreadsheet
            sample_data = [
                ['ID', 'Name', 'Email', 'Department', 'Created Date'],
                [1, 'John Doe', 'john.doe@example.com', 'Engineering', datetime.datetime.now().strftime('%Y-%m-%d')],
                [2, 'Jane Smith', 'jane.smith@example.com', 'Marketing', datetime.datetime.now().strftime('%Y-%m-%d')],
                [3, 'Bob Johnson', 'bob.johnson@example.com', 'Finance', datetime.datetime.now().strftime('%Y-%m-%d')],
                [4, 'Alice Brown', 'alice.brown@example.com', 'HR', datetime.datetime.now().strftime('%Y-%m-%d')],
                [5, 'David Wilson', 'david.wilson@example.com', 'Operations', datetime.datetime.now().strftime('%Y-%m-%d')]
            ]
            
            # Update values in the spreadsheet
            body = {
                'values': sample_data
            }
            
            self.sheets_service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range='Sample Data!A1:E6',
                valueInputOption='RAW',
                body=body
            ).execute()
            
            # Format the header row in bold
            format_request = {
                'requests': [
                    {
                        'repeatCell': {
                            'range': {
                                'sheetId': 0,
                                'startRowIndex': 0,
                                'endRowIndex': 1,
                                'startColumnIndex': 0,
                                'endColumnIndex': 5
                            },
                            'cell': {
                                'userEnteredFormat': {
                                    'textFormat': {
                                        'bold': True
                                    }
                                }
                            },
                            'fields': 'userEnteredFormat.textFormat.bold'
                        }
                    },
                    {
                        'updateSheetProperties': {
                            'properties': {
                                'sheetId': 0,
                                'gridProperties': {
                                    'frozenRowCount': 1
                                }
                            },
                            'fields': 'gridProperties.frozenRowCount'
                        }
                    }
                ]
            }
            
            self.sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=format_request
            ).execute()
            
            # Get the link to the spreadsheet
            spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
            
            self.logger.info(f"Created test spreadsheet '{spreadsheet_name}' with ID: {spreadsheet_id}")
            self.logger.info(f"Spreadsheet URL: {spreadsheet_url}")
            
            return spreadsheet_id
            
        except Exception as e:
            self.logger.error(f"Error creating test spreadsheet: {str(e)}")
            return None
    
    def get_folder_details(self, folder_id: str) -> Dict[str, Any]:
        """
        Get details about a Google Drive folder
        
        Args:
            folder_id: ID of the Google Drive folder
            
        Returns:
            Dictionary with folder details
        """
        if not self.drive_service:
            if not self.initialize():
                self.logger.error("Failed to initialize Google services")
                return {}
                
        try:
            # Get folder metadata
            folder = self.drive_service.files().get(
                fileId=folder_id,
                fields='id, name, mimeType, createdTime, modifiedTime'
            ).execute()
            
            return folder
            
        except Exception as e:
            self.logger.error(f"Error getting folder details: {str(e)}")
            return {}


def main():
    """Main entry point for the Google Sheets Explorer script"""
    parser = argparse.ArgumentParser(description="Google Sheets Explorer")
    parser.add_argument(
        "--credentials",
        required=False,
        help="Path to Google API credentials file (if not specified, will search in default locations)"
    )
    parser.add_argument(
        "--token",
        default=DEFAULT_TOKEN_FILE,
        help=f"Path to Google API token file (default: {DEFAULT_TOKEN_FILE})"
    )
    parser.add_argument(
        "--folder",
        required=True,
        help="Google Drive folder ID to explore"
    )
    parser.add_argument(
        "--create-test",
        action="store_true",
        help="Create a test spreadsheet in the folder"
    )
    parser.add_argument(
        "--name",
        help="Name for the test spreadsheet (if --create-test is used)"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize the explorer
        explorer = GoogleSheetsExplorer(
            credentials_file=args.credentials,
            token_file=args.token
        )
        
        if not explorer.initialize():
            logger.error("Failed to initialize Google Sheets Explorer")
            sys.exit(1)
        
        # Get folder details
        folder_details = explorer.get_folder_details(args.folder)
        if folder_details:
            logger.info(f"Folder: {folder_details.get('name')} (ID: {folder_details.get('id')})")
        else:
            logger.error(f"Failed to get details for folder ID: {args.folder}")
            sys.exit(1)
        
        # List files in the folder
        files = explorer.list_files(args.folder)
        if files:
            logger.info("\nGoogle Sheets files in folder:")
            for i, file in enumerate(files, 1):
                modified_time = file.get('modifiedTime', 'Unknown')
                created_time = file.get('createdTime', 'Unknown')
                logger.info(f"{i}. {file.get('name')} (ID: {file.get('id')})")
                logger.info(f"   Created: {created_time}, Modified: {modified_time}")
        else:
            logger.info("No Google Sheets files found in the folder")
        
        # Create test spreadsheet if requested
        if args.create_test:
            spreadsheet_id = explorer.create_test_spreadsheet(args.folder, args.name)
            if spreadsheet_id:
                logger.info(f"\nTest spreadsheet created with ID: {spreadsheet_id}")
                logger.info(f"URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
            else:
                logger.error("Failed to create test spreadsheet")
                sys.exit(1)
                
    except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(1)
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 