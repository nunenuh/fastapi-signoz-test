"""Configuration module for the application."""

from typing import Dict, List

from pydantic import Field
from pydantic_settings import BaseSettings

# from .tracer import LangchainTracer


class Settings(BaseSettings):
    """Application settings and configuration."""

    # Application Settings
    API_V1_STR: str = Field(default="/api/v1", env="API_V1_STR")
    PROJECT_NAME: str = Field(default="TabLogs OCR Service", env="PROJECT_NAME")
    VERSION: str = Field(default="0.1.0", env="VERSION")
    VERSION_TAG: str = Field(default="latest")

    # Server Settings
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8081, env="PORT")
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"]
    )
    
    # Environment Settings
    ENVIRONMENT: str = Field(default="dev", env="ENVIRONMENT")
    DEBUG: bool = Field(default=False, env="DEBUG")

    # OpenTelemetry Settings
    ENABLE_TELEMETRY: bool = Field(default=True, env="ENABLE_TELEMETRY")
    OTEL_EXPORTER_OTLP_ENDPOINT: str = Field(
        default="http://localhost:4317",  # SigNoz default endpoint
        env="OTEL_EXPORTER_OTLP_ENDPOINT"
    )
    OTEL_EXPORTER_OTLP_INSECURE: bool = Field(
        default=True,  # Set to False in production
        env="OTEL_EXPORTER_OTLP_INSECURE"
    )
    OTEL_SERVICE_NAME: str = Field(
        default="fastapi-signoz-service",
        env="OTEL_SERVICE_NAME"
    )
    OTEL_RESOURCE_ATTRIBUTES: Dict[str, str] = Field(
        default={
            "service.name": "fastapi-signoz-service",
            "service.version": "0.1.0",
            "deployment.environment": "dev",
        }
    )
    OTEL_EXCLUDED_URLS: str = Field(
        default="/health,/metrics,/docs,/openapi.json",
        env="OTEL_EXCLUDED_URLS"
    )
    OTEL_TRACES_SAMPLER: str = Field(
        default="always_on",
        env="OTEL_TRACES_SAMPLER"
    )
    OTEL_INSTRUMENTED_LIBRARIES: List[str] = Field(
        default=["fastapi", "requests", "logging", "httpx", "sqlalchemy"],
    )
    OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED: bool = Field(
        default=True,
        env="OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED"
    )

    class Config:
        """Pydantic configuration."""

        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"
        extra = "allow"


settings = Settings()