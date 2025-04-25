"""Health check schemas module."""

from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    """Base response model with generic data field."""

    status: int = 200
    message: str = "success"
    data: Optional[T] = None


class PingData(BaseModel):
    """Ping response data model."""

    status: str = "ok"
    message: str = "pong"
    environment: str
    version: Optional[str] = "1.0.0"


class HealthData(BaseModel):
    """Health check response data model."""

    status: str
    environment: str
    services: dict[str, str]


class PingResponse(ResponseModel[PingData]):
    """Ping endpoint response model."""


class HealthResponse(ResponseModel[HealthData]):
    """Health check endpoint response model."""


__all__ = ["PingResponse", "HealthResponse", "PingData", "HealthData"]
