"""API router to manage all routes."""

from fastapi import APIRouter

from feptm.api.v1 import projects, specialists, timesheets, periods, reports

# Create API router
router = APIRouter()

# Include routers from different modules
router.include_router(
    projects.router, prefix="/projects", tags=["projects"]
)
router.include_router(
    specialists.router, prefix="/specialists", tags=["specialists"]
)
router.include_router(
    timesheets.router, prefix="/timesheets", tags=["timesheets"]
)
router.include_router(
    periods.router, prefix="/periods", tags=["periods"]
)
router.include_router(
    reports.router, prefix="/reports", tags=["reports"]
) 