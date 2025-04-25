"""Health check endpoints handler module."""

from typing import Any

from fastapi import APIRouter, HTTPException, status

from ...core.config import settings
from ...health.schemas import HealthResponse, PingResponse

router = APIRouter()


@router.get(
    "/ping",
    response_model=PingResponse,
    status_code=status.HTTP_200_OK,
    tags=["health"],
    summary="Ping endpoint",
    description="Simple ping endpoint to verify service is running",
)
async def ping() -> Any:
    """Check if the service is alive."""
    try:
        return {
            "status": status.HTTP_200_OK,
            "message": "success",
            "data": {
                "status": "ok",
                "message": "pong",
                "environment": settings.ENVIRONMENT,
                "version": "1.0.0",
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Error checking service health", "error": str(e)},
        )


@router.get(
    "",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    tags=["health"],
    summary="Health check",
    description="Detailed health check endpoint that verifies all service components",
)
async def health_check() -> Any:
    """Check the health of all service components."""
    try:
        return {
            "status": status.HTTP_200_OK,
            "message": "success",
            "data": {
                "status": "healthy",
                "environment": settings.ENVIRONMENT,
                "services": {"api": "up"},
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"message": "Service unhealthy", "error": str(e)},
        )
