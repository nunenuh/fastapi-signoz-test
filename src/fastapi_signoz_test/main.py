"""Main application module for the OCR service."""

import logging

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from .core.config import settings
from .core.telemetry import setup_telemetry
from .router import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

log = logging.getLogger("uvicorn")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Initialize OpenTelemetry
setup_telemetry(app)

app.include_router(api_router, prefix=settings.API_V1_STR)

# # Setup Langchain tracing
# tracer = settings.setup_langchain()

# # Store tracer in app state for use in other parts of application
# app.state.langchain_tracer = tracer


@app.on_event("startup")
async def startup_event():
    """Log startup of the application."""
    log.info("Starting up OCR service...")


@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown of the application."""
    log.info("Shutting down OCR service...")


if __name__ == "__main__":
    uvicorn.run(
        "main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG
    )
