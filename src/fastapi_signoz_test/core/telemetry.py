"""OpenTelemetry instrumentation module for the application."""

import logging
import os
from typing import Dict, List, Optional

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION, DEPLOYMENT_ENVIRONMENT
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from .config import settings

logger = logging.getLogger(__name__)


def setup_telemetry(app: FastAPI) -> None:
    """Configure OpenTelemetry instrumentation for the application.
    
    Args:
        app: FastAPI application instance
    """
    if not settings.ENABLE_TELEMETRY:
        logger.info("Telemetry is disabled. Skipping instrumentation setup.")
        return

    logger.info("Setting up OpenTelemetry instrumentation")
    
    # Set environment variable for auto-instrumentation of logging
    if settings.OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED:
        os.environ["OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED"] = "true"
        logger.info("Logging auto-instrumentation is enabled")
    
    # Check if app is already instrumented when running with opentelemetry-instrument
    if hasattr(app, "_is_instrumented_by_opentelemetry") and app._is_instrumented_by_opentelemetry:
        logger.info("Application already instrumented by OpenTelemetry auto-instrumentation")
        return
    
    # Check if there's already a global tracer provider set by auto-instrumentation
    current_tracer_provider = trace.get_tracer_provider()
    if getattr(current_tracer_provider, "__class__", None).__name__ == "TracerProvider":
        logger.info("Using existing OpenTelemetry TracerProvider from auto-instrumentation")
        tracer_provider = current_tracer_provider
    else:
        # Create basic resource attributes
        resource_attributes = {
            SERVICE_NAME: settings.OTEL_SERVICE_NAME or "fastapi-signoz-service",
            SERVICE_VERSION: settings.VERSION or "0.1.0",
            DEPLOYMENT_ENVIRONMENT: settings.ENVIRONMENT or "dev",
        }
        
        # Add additional attributes from settings.OTEL_RESOURCE_ATTRIBUTES
        if settings.OTEL_RESOURCE_ATTRIBUTES:
            for key, value in settings.OTEL_RESOURCE_ATTRIBUTES.items():
                if key not in resource_attributes:  # Don't override the core attributes
                    resource_attributes[key] = value
        
        # Create resource and log it
        resource = Resource.create(resource_attributes)
        logger.info(f"Created OpenTelemetry resource with attributes: {resource_attributes}")

        # Create and set tracer provider
        tracer_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(tracer_provider)
        
        # Configure exporter
        otlp_exporter = OTLPSpanExporter(
            endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT,
            insecure=settings.OTEL_EXPORTER_OTLP_INSECURE,
        )
        logger.info(f"Configured OTLP exporter with endpoint: {settings.OTEL_EXPORTER_OTLP_ENDPOINT}")
        
        # Add span processor
        tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    
    # Check if FastAPI app is already instrumented
    if not hasattr(app, "_is_instrumented") or not app._is_instrumented:
        logger.info("Instrumenting FastAPI application")
        # Instrument FastAPI
        FastAPIInstrumentor.instrument_app(
            app,
            tracer_provider=tracer_provider,
            excluded_urls=settings.OTEL_EXCLUDED_URLS
        )
    else:
        logger.info("FastAPI application already instrumented")
    
    # Set the flag to avoid double instrumentation
    app._is_instrumented_by_opentelemetry = True
    
    # Instrument other libraries if not already instrumented by auto-instrumentation
    _instrument_libraries(settings.OTEL_INSTRUMENTED_LIBRARIES, tracer_provider)
    
    logger.info("OpenTelemetry instrumentation setup completed")


def _instrument_libraries(libraries: List[str], tracer_provider: TracerProvider) -> None:
    """Instrument specified libraries with OpenTelemetry.
    
    Args:
        libraries: List of library names to instrument
        tracer_provider: TracerProvider instance
    """
    for library in libraries:
        try:
            if library.lower() == "logging":
                if not getattr(LoggingInstrumentor, "_is_instrumented", False):
                    LoggingInstrumentor().instrument(tracer_provider=tracer_provider)
                    logger.debug("Instrumented logging library")
                    # Set the instrumented flag
                    setattr(LoggingInstrumentor, "_is_instrumented", True)
            
            elif library.lower() == "requests":
                if not getattr(RequestsInstrumentor, "_is_instrumented", False):
                    RequestsInstrumentor().instrument(tracer_provider=tracer_provider)
                    logger.debug("Instrumented requests library")
                    # Set the instrumented flag
                    setattr(RequestsInstrumentor, "_is_instrumented", True)
            
            elif library.lower() == "httpx":
                if not getattr(HTTPXClientInstrumentor, "_is_instrumented", False):
                    HTTPXClientInstrumentor().instrument(tracer_provider=tracer_provider)
                    logger.debug("Instrumented httpx library")
                    # Set the instrumented flag
                    setattr(HTTPXClientInstrumentor, "_is_instrumented", True)
            
            # Add more library instrumentation here as needed
            
        except Exception as e:
            logger.error(f"Failed to instrument {library}: {str(e)}")


def create_span(name: str, attributes: Optional[Dict] = None) -> None:
    """Create a custom span for a specific operation.
    
    Args:
        name: Span name
        attributes: Optional span attributes
    
    Returns:
        Created span
    """
    tracer = trace.get_tracer(__name__)
    attributes = attributes or {}
    
    return tracer.start_as_current_span(name, attributes=attributes) 