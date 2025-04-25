"""OpenTelemetry configuration module."""

import asyncio
import logging
import socket
from typing import Optional, Callable, Any, Dict

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
# Add additional instrumentations as needed
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter, SimpleSpanProcessor

from .config import settings

logger = logging.getLogger(__name__)


class TelemetryMiddleware(BaseHTTPMiddleware):
    """Add custom telemetry data to requests."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Get current span from request
        current_span = trace.get_current_span()
        
        # Add request info to span
        if current_span.is_recording():
            # Add custom attributes
            current_span.set_attribute("http.request.path", request.url.path)
            current_span.set_attribute("http.request.query", str(request.url.query))
            
            # Add select headers (avoid sensitive data)
            for header in ["user-agent", "content-type", "accept"]:
                if header in request.headers:
                    current_span.set_attribute(
                        f"http.request.header.{header}", request.headers[header]
                    )
        
        # Process the request
        response = await call_next(request)
        
        # Add response info to span
        if current_span.is_recording():
            current_span.set_attribute("http.response.status_code", response.status_code)
            if "content-type" in response.headers:
                current_span.set_attribute(
                    "http.response.content_type", response.headers["content-type"]
                )
        
        return response


def create_resource(service_name: str) -> Resource:
    """Create a resource with service and environment information."""
    hostname = socket.gethostname()
    
    # Create base attributes
    attributes = {
        "service.name": service_name,
        "service.version": settings.VERSION,
        "deployment.environment": settings.ENVIRONMENT,
        "host.name": hostname,
        "telemetry.sdk.language": "python",
    }
    
    # Add any additional environment-specific attributes
    if settings.ENVIRONMENT == "production":
        # Add production-specific attributes
        pass
    elif settings.ENVIRONMENT == "staging":
        # Add staging-specific attributes
        pass
    
    return Resource.create(attributes)


def setup_exporters(tracer_provider: TracerProvider) -> None:
    """Configure and attach exporters to the tracer provider."""
    try:
        # Create OTLP exporter
        otlp_exporter = OTLPSpanExporter(
            endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT,
            insecure=settings.OTEL_EXPORTER_OTLP_INSECURE,
        )
        
        # Add span processor
        span_processor = BatchSpanProcessor(
            otlp_exporter,
            # Optimize batch processing
            max_export_batch_size=512,
            schedule_delay_millis=5000
        )
        tracer_provider.add_span_processor(span_processor)
        logger.info(f"OTLP exporter configured for endpoint: {settings.OTEL_EXPORTER_OTLP_ENDPOINT}")
        
        # Optionally add console exporter for debugging
        if settings.ENVIRONMENT in ["development", "local"]:
            console_exporter = ConsoleSpanExporter()
            tracer_provider.add_span_processor(SimpleSpanProcessor(console_exporter))
            logger.debug("Console exporter added for local debugging")
            
    except Exception as e:
        logger.warning(f"Failed to initialize OpenTelemetry OTLP exporter: {e}")
        logger.warning("Falling back to console exporter only")
        console_exporter = ConsoleSpanExporter()
        tracer_provider.add_span_processor(SimpleSpanProcessor(console_exporter))


def setup_instrumentations() -> None:
    """Set up all required instrumentations."""
    # Standard instrumentations
    RequestsInstrumentor().instrument()
    LoggingInstrumentor().instrument()
    
    # Add additional instrumentations as needed
    try:
        # Optional instrumentations based on what's installed
        # Only import if you're using these libraries
        from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentor
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
        from opentelemetry.instrumentation.redis import RedisInstrumentor
        
        # Instrument aiohttp client
        try:
            AioHttpClientInstrumentor().instrument()
            logger.debug("AioHttp client instrumentation enabled")
        except Exception:
            pass
            
        # Instrument SQLAlchemy
        try:
            SQLAlchemyInstrumentor().instrument()
            logger.debug("SQLAlchemy instrumentation enabled")
        except Exception:
            pass
            
        # Instrument Redis
        try:
            RedisInstrumentor().instrument()
            logger.debug("Redis instrumentation enabled")
        except Exception:
            pass
            
    except ImportError:
        # Libraries not installed, that's fine
        pass


def shutdown_telemetry() -> None:
    """Properly shut down OpenTelemetry to flush pending spans."""
    tracer_provider = trace.get_tracer_provider()
    if hasattr(tracer_provider, "shutdown"):
        tracer_provider.shutdown()
        logger.info("OpenTelemetry telemetry shut down cleanly")


def setup_telemetry(app: FastAPI, service_name: Optional[str] = None) -> None:
    """
    Initialize OpenTelemetry with SigNoz configuration.
    
    Args:
        app: FastAPI application instance
        service_name: Optional service name override
    """
    if not settings.ENABLE_TELEMETRY:
        logger.info("Telemetry is disabled. Skipping OpenTelemetry setup.")
        return

    service_name = service_name or settings.PROJECT_NAME
    
    # Create a resource with service name and other attributes
    resource = create_resource(service_name)

    # Create a tracer provider
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    # Setup exporters (OTLP, console, etc.)
    setup_exporters(tracer_provider)
    
    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer_provider)
    
    # Setup all other instrumentations
    setup_instrumentations()
    
    # Add custom middleware for additional request/response details
    app.add_middleware(TelemetryMiddleware)
    
    # Register shutdown handler
    app.add_event_handler("shutdown", shutdown_telemetry)

    logger.info(f"OpenTelemetry initialized for service: {service_name}")


def get_tracer(module_name: str) -> trace.Tracer:
    """Get a tracer for a specific module."""
    return trace.get_tracer(module_name)


def traced(func: Callable) -> Callable:
    """Simple decorator to add tracing to a function."""
    async def async_wrapper(*args: Any, **kwargs: Dict[str, Any]) -> Any:
        tracer = get_tracer(func.__module__)
        with tracer.start_as_current_span(func.__name__):
            return await func(*args, **kwargs)

    def sync_wrapper(*args: Any, **kwargs: Dict[str, Any]) -> Any:
        tracer = get_tracer(func.__module__)
        with tracer.start_as_current_span(func.__name__):
            return func(*args, **kwargs)

    # Check if function is async or sync
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper 