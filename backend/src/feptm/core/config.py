"""Configuration settings for the application."""

import os
from pathlib import Path
from typing import Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Project info
    PROJECT_NAME: str = "Time & Materials Accounting API"
    PROJECT_DESCRIPTION: str = (
        "Backend service for time and materials accounting with Google Sheets"
    )
    VERSION: str = "0.1.0"

    # Base directory
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent

    # API settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    API_KEY: Optional[str] = None

    # Google API settings
    GOOGLE_CREDENTIALS_FILE: Optional[Path] = (
        Path(__file__).resolve().parent.parent.parent.parent / "credentials.json"
        if (
            Path(__file__).resolve().parent.parent.parent.parent / "credentials.json"
        ).exists()
        else None
    )
    GOOGLE_TOKEN_FILE: Optional[Path] = Path(os.environ.get('HOME', os.path.expanduser('~'))) / ".google_sheets_token.json"
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_TIMESHEET_TEMPLATE_ID: Optional[str] = None
    GOOGLE_REPORT_TEMPLATE_ID: Optional[str] = None

    # Google Drive settings for projects
    # Important: make sure all these files are accessible to the user
    # authenticated via OAuth (enable "Share by link" access)
    GOOGLE_PROJECTS_FOLDER_ID: Optional[str] = (
        None  # Specify the Google Drive folder ID here
    )

    # Google Sheets templates - specify your identifiers here or update environment variables
    # To make templates accessible, "Share by link" must be enabled for them (Share > General Access)
    GOOGLE_PROJECT_INFO_TEMPLATE_ID: Optional[str] = None
    GOOGLE_PROJECT_REPORT_TEMPLATE_ID: Optional[str] = None
    GOOGLE_PROJECT_CALCULATIONS_TEMPLATE_ID: Optional[str] = None

    # Model configurations
    SPECIALIST_ROLES: list[str] = Field(
        default=["Developer", "QA", "Designer", "Project Manager", "DevOps"]
    )

    @validator("GOOGLE_TOKEN_FILE", pre=True)
    def expand_user_path(cls, v):
        """Expand user home directory in path string if needed."""
        if isinstance(v, str) and v.startswith("~"):
            return os.path.expanduser(v)
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )


# Load settings
settings = Settings()
