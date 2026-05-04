"""
## Digital Hospital -- Core Service

Master service for persons, relationships and catalogues.
Owns the `people` and `relationships` schemas.

### Core Responsibilities
1. **Person Management** -- CRUD for persons (patients, doctors, staff).
2. **Contact Information** -- Email, phone, address management.
3. **Identity Documents** -- CURP, national ID, and other identifiers.
4. **Relationships** -- Family and social connections between persons.

### Dependencies
- **PostgreSQL**: people, relationships schemas via dh_shared.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import text

from dh_shared.models.people import PeopleBase
from dh_shared.models.expedient import ExpedientBase
import dh_shared.models.people      # noqa
import dh_shared.models.expedient   # noqa

from app.settings.config import settings
from app.shared.database.postgres import engine
from app.shared.utils.logger import logger
from app.contexts.people.infrastructure.api.v1.router import (
    people_router, contact_router, identity_router, social_router,
    address_router, validation_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Sync database schemas on startup."""
    await logger.info("Starting dh_core...", event="app.startup")
    try:
        async with engine.begin() as conn:
            await conn.execute(text("CREATE SCHEMA IF NOT EXISTS expedient"))
            await conn.execute(text("CREATE SCHEMA IF NOT EXISTS people"))
            await conn.run_sync(ExpedientBase.metadata.create_all)
            await conn.run_sync(PeopleBase.metadata.create_all)
        await logger.info("Schemas synced.", event="app.startup.done")
    except Exception as e:
        await logger.error(f"DB unavailable: {e}", event="app.startup.error")
    yield
    await engine.dispose()
    await logger.info("dh_core stopped.", event="app.shutdown")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=__doc__,
    version=settings.VERSION,
    lifespan=lifespan,
    openapi_tags=[
        {"name": "Health", "description": "Service health check."},
        {"name": "People", "description": "Person CRUD and status updates."},
        {"name": "Address", "description": "Address management for persons."},
        {"name": "Contact", "description": "Email and phone management for persons."},
        {"name": "Identity", "description": "Personal identifiers (CURP, RFC, etc.)."},
        {"name": "Social", "description": "Emergency contacts and social links."},
        {"name": "Validation", "description": "Registration field conflict checks."},
    ],
)

app.include_router(people_router, prefix="/v1")
app.include_router(address_router, prefix="/v1")
app.include_router(contact_router, prefix="/v1")
app.include_router(identity_router, prefix="/v1")
app.include_router(social_router, prefix="/v1")
app.include_router(validation_router, prefix="/v1")

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/", tags=["UI"])
async def root():
    """Serve the test UI page."""
    return FileResponse("app/static/index.html")


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "dh_core"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8040)
