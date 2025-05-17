"""Service for working with configuration settings from Google Sheets."""

from enum import Enum, auto
from typing import Dict, Any, cast

from feptm.core.config import settings
from feptm.core.log import log
from feptm.services.google_sheets_service import google_sheets_service


class FormulaName(Enum):
    """Enumeration of available formula names in the configuration sheet."""
    
    CALCULATE_WORKING_HOURS = "Calculate working hours"
    IMPORT_SPECIALIST_TIMESHEET = "Import specialist timesheet" 
    GROSS_TOTAL_COST = "Gross total cost"
    NET_TOTAL_COST = "Net total cost"
    REVENUE = "Revenue"


class ConfigService:
    """Service for accessing configuration from Google Sheets."""

    def __init__(self):
        """Initialize the service."""
        self.google_sheets_service = google_sheets_service
        self._formula_cache: Dict[str, str] = {}
        
    def get_formula(self, formula_name: FormulaName) -> str:
        """Get a formula by name from the configuration spreadsheet.
        
        Args:
            formula_name: Enum value for the formula to retrieve
            
        Returns:
            The formula value
            
        Raises:
            Exception: If formula not found or configuration sheet not set
        """
        # Check if formula is in cache
        formula_key = formula_name.value
        if formula_key in self._formula_cache:
            return self._formula_cache[formula_key]
            
        # Not in cache, need to retrieve it
        if not settings.GOOGLE_CONFIG_SHEET_ID:
            raise Exception("GOOGLE_CONFIG_SHEET_ID not set in environment variables")
            
        if not self.google_sheets_service.is_initialized():
            raise Exception("Google Sheets service not initialized")
            
        try:
            # Find the "Formulas" sheet
            sheet = self.google_sheets_service.get_sheet_by_name(
                spreadsheet_id=settings.GOOGLE_CONFIG_SHEET_ID,
                sheet_name="Formulas"
            )
            
            if not sheet:
                raise Exception("Formulas sheet not found in the configuration spreadsheet")
                
            # Get the formulas data
            result = (
                self.google_sheets_service.sheets_service.spreadsheets()
                .values()
                .get(spreadsheetId=settings.GOOGLE_CONFIG_SHEET_ID, range="Formulas!A:C")
                .execute()
            )
                
            values = result.get("values", [])
            if not values or len(values) <= 1:  # Check if we have data (besides header)
                raise Exception("No formulas found in the configuration spreadsheet")
                
            # Skip header row and process formulas
            for row in values[1:]:
                if len(row) >= 2:  # Should have at least formula name and value
                    current_formula_name = row[0].strip()
                    formula_value = row[1].strip()
                    
                    # Add to cache regardless if it's the one we're looking for
                    if formula_value:
                        self._formula_cache[current_formula_name] = formula_value
                    
                    # If this is the formula we're looking for, return it
                    if current_formula_name == formula_key and formula_value:
                        return formula_value
                        
            # If we get here, the formula was not found
            raise Exception(f"Formula '{formula_key}' not found in configuration spreadsheet")
                
        except Exception as e:
            log.error(f"Error getting formula: {str(e)}")
            raise
            
    def get_import_specialist_timesheet_formula(self, specialist_timesheet_id: str) -> str:
        """Get the Import specialist timesheet formula with specialist's timesheet ID.
        
        Args:
            specialist_timesheet_id: ID of the specialist's timesheet to use in the formula
            
        Returns:
            The formula with the specialist's timesheet ID inserted
            
        Raises:
            Exception: If formula not found
        """
        formula = self.get_formula(FormulaName.IMPORT_SPECIALIST_TIMESHEET)
        return formula.replace("SpecialistSpreadsheetID", specialist_timesheet_id)


# Create singleton instance
config_service = ConfigService() 