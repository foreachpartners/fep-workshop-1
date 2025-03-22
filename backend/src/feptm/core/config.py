"""Configuration settings for the application."""

import os
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Project info
    PROJECT_NAME: str = "Time & Materials Accounting API"
    PROJECT_DESCRIPTION: str = "Backend service for time and materials accounting with Google Sheets"
    VERSION: str = "0.1.0"

    # Base directory
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent

    # API settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    API_KEY: Optional[str] = None

    # Google API settings
    GOOGLE_CREDENTIALS_FILE: Optional[Path] = None
    GOOGLE_TOKEN_FILE: Optional[Path] = None
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_TIMESHEET_TEMPLATE_ID: Optional[str] = None
    GOOGLE_REPORT_TEMPLATE_ID: Optional[str] = None

    # Model configurations
    SPECIALIST_ROLES: list[str] = Field(
        default=["Developer", "QA", "Designer", "Project Manager", "DevOps"]
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )


# Load settings
settings = Settings() 