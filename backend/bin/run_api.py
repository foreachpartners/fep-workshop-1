#!/usr/bin/env python
"""Script to run the FastAPI application."""

import uvicorn

from feptm.core.config import settings
from feptm.main import app


if __name__ == "__main__":
    uvicorn.run(
        "feptm.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    ) 