"""Health check endpoint."""

from datetime import datetime, timezone

from fastapi import APIRouter

from app.core.config import settings
from app.schemas.common import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Return the current health status of the API.

    This endpoint can be used by load balancers, monitoring tools,
    and Docker health checks to verify the service is running.
    """
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        timestamp=datetime.now(timezone.utc),
    )
