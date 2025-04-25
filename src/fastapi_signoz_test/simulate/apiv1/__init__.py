"""API v1 router initialization."""

from fastapi import APIRouter

from fastapi_signoz_test.simulate.apiv1.handler import router as handler_router

router = APIRouter(prefix="/api/v1")
router.include_router(handler_router)
