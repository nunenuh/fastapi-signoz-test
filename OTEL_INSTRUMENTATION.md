# OpenTelemetry Instrumentation for FastAPI

This document describes how to use OpenTelemetry instrumentation with the FastAPI application to send telemetry data to SigNoz or another OpenTelemetry backend.

## Auto-Instrumentation

OpenTelemetry provides an easy way to automatically instrument your Python application using the `opentelemetry-instrument` command line tool. This approach requires minimal code changes.

### Required Packages

The following packages are required for OpenTelemetry instrumentation:

```bash
# Core packages
opentelemetry-distro[otlp]
opentelemetry-api
opentelemetry-sdk

# FastAPI specific instrumentation
opentelemetry-instrumentation-fastapi
opentelemetry-instrumentation-httpx
opentelemetry-instrumentation-requests
opentelemetry-instrumentation-logging

# Optional but useful
opentelemetry-instrumentation-sqlalchemy
```

### Running with Auto-Instrumentation

You can run the application with auto-instrumentation using one of the following methods:

#### 1. Using the Makefile

```bash
# This will automatically configure and run the application with OpenTelemetry
make run-instrumented
```

#### 2. Using the Provided Shell Script

```bash
# Make sure the script is executable
chmod +x run_instrumented.sh

# Run the script
./run_instrumented.sh
```

#### 3. Manually with Environment Variables

```bash
# Set required environment variables
export OTEL_RESOURCE_ATTRIBUTES="service.name=fastapi-signoz-service,service.version=0.1.0,deployment.environment=dev"
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"  # Update this with your SigNoz/collector endpoint
export OTEL_EXPORTER_OTLP_INSECURE="true"
export OTEL_EXPORTER_OTLP_PROTOCOL="grpc"
export OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED="true"

# Run with the opentelemetry-instrument command
opentelemetry-instrument uvicorn src.fastapi_signoz_test.main:app --host 0.0.0.0 --port 8081
```

## Configuration Options

The application supports various OpenTelemetry configuration options through environment variables:

| Environment Variable | Description | Default Value |
| --- | --- | --- |
| ENABLE_TELEMETRY | Enable/disable telemetry | true |
| OTEL_EXPORTER_OTLP_ENDPOINT | OpenTelemetry collector endpoint | http://localhost:4317 |
| OTEL_EXPORTER_OTLP_INSECURE | Allow insecure connections | true |
| OTEL_SERVICE_NAME | Service name for telemetry | fastapi-signoz-service |
| OTEL_RESOURCE_ATTRIBUTES | Resource attributes for the service | service.name=fastapi-signoz-service,service.version=0.1.0,deployment.environment=dev |
| OTEL_EXCLUDED_URLS | URLs to exclude from instrumentation | /health,/metrics,/docs,/openapi.json |
| OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED | Enable logging auto-instrumentation | true |

## SigNoz Cloud Configuration

If you're using SigNoz Cloud, update the `run_instrumented.sh` script with your SigNoz Cloud ingestion key:

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT="https://ingest.{region}.signoz.cloud:443"
export OTEL_EXPORTER_OTLP_HEADERS="signoz-access-token=<your-signoz-ingestion-key>"
export OTEL_EXPORTER_OTLP_PROTOCOL="grpc"
```

## Debugging

If you want to see the telemetry data in the console (useful for debugging), add these environment variables:

```bash
export OTEL_TRACES_EXPORTER="console,otlp"
export OTEL_METRICS_EXPORTER="console,otlp"
export OTEL_LOGS_EXPORTER="console,otlp"
```

## Manual Instrumentation

For more advanced use cases, the application includes a `telemetry.py` module that allows for manual instrumentation. You can create custom spans using the `create_span` function:

```python
from fastapi_signoz_test.core.telemetry import create_span

# In your code:
with create_span("custom_operation", attributes={"key": "value"}):
    # Your code here
    pass
```

## References

- [OpenTelemetry Python Documentation](https://opentelemetry-python.readthedocs.io/)
- [SigNoz OpenTelemetry Python Example](https://github.com/SigNoz/opentelemetry-python-example)