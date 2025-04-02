from fastapi import FastAPI

from src.routes import (
    notes_router,
    analytics_router,
    ai_router,
)

app = FastAPI(
    title="Notes management API",
    description="API for managing notes, including CRUD and analytics"
)

api_version_prefix = "/api/v1"

app.include_router(
    notes_router, prefix=f"{api_version_prefix}/notes", tags=["notes"]
)
app.include_router(
    analytics_router, prefix=f"{api_version_prefix}/analytics", tags=["analytics"]
)
app.include_router(
    ai_router, prefix=f"{api_version_prefix}/ai", tags=["ai"]
)
