"""Main router module for the application."""

from fastapi import APIRouter

from .health.apiv1.handler import router as health_router
from .simulate.apiv1.handler import router as simulate_router

api_router = APIRouter()

api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(simulate_router, prefix="/simulate", tags=["simulate"])
