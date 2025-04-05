"""Helper functions for working with Google Sheets."""

from pathlib import Path
from typing import Dict, Optional, Any


def find_credentials_file() -> str:
    """Find the credentials file in default locations.
    
    Returns:
        Path to the credentials file
        
    Raises:
        FileNotFoundError: If no credentials file can be found
    """
    default_locations = [
        "backend/credentials.json",
    ]
    
    # Check default locations
    for location in default_locations:
        if Path(location).is_file():
            return str(location)
    
    # If we get here, no credentials file was found
    locations_str = "\n- ".join([""] + default_locations)
    raise FileNotFoundError(
        f"Could not find Google API credentials file. "
        f"Please place credentials.json in one of the following locations:{locations_str}"
    )


def get_sheet_by_name(sheets_service, spreadsheet_id: str, sheet_name: str) -> Optional[Dict[str, Any]]:
    """Finds a sheet in the spreadsheet by its name.
    
    Args:
        sheets_service: Google Sheets service instance
        spreadsheet_id: ID of the spreadsheet
        sheet_name: Name of the sheet to find
        
    Returns:
        Dictionary with information about the found sheet or None if not found
    """
    try:
        # Get spreadsheet metadata
        spreadsheet_metadata = sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id
        ).execute()
        
        # Get list of sheets
        sheets = spreadsheet_metadata.get('sheets', [])
        if not sheets:
            print(f"Warning: No sheets found in the spreadsheet with ID {spreadsheet_id}")
            return None
        
        # Find sheet with specified name
        target_sheet = None
        available_sheets = []
        for sheet in sheets:
            sheet_title = sheet['properties']['title']
            available_sheets.append(sheet_title)
            if sheet_title == sheet_name:
                target_sheet = sheet
                break
        
        if not target_sheet:
            print(f"Warning: Sheet '{sheet_name}' not found. Available sheets: {', '.join(available_sheets)}")
            return None
        
        return target_sheet
        
    except Exception as error:
        print(f"Error getting sheet by name: {error}")
        return None 