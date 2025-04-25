"""Complex workflow simulation module with OpenTelemetry instrumentation."""

import asyncio
import random
from typing import List, Optional, Dict, Any

from fastapi import HTTPException, status
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from ..schemas import StepConfig, OperationType

tracer = trace.get_tracer(__name__)


class Step:
    """Base step class for workflow steps with OpenTelemetry instrumentation."""

    def __init__(
        self,
        name: str,
        operation_type: str,
        duration_range: tuple[float, float] = (0.1, 0.5),
        parallel: bool = False,
        substeps: Optional[List['Step']] = None,
        attributes: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.operation_type = operation_type
        self.duration_range = duration_range
        self.parallel = parallel
        self.substeps = substeps or []
        self.attributes = attributes or {}
        self.status: Optional[str] = None
        self.error: Optional[str] = None

    async def execute(self) -> None:
        """Execute the step with OpenTelemetry tracing."""
        with tracer.start_as_current_span(
            self.name,
            attributes={
                "step.name": self.name,
                "step.type": self.operation_type,
                **self.attributes
            },
        ) as span:
            try:
                # Execute substeps if any
                if self.substeps:
                    if self.parallel:
                        tasks = [step.execute() for step in self.substeps]
                        await asyncio.gather(*tasks)
                    else:
                        for step in self.substeps:
                            await step.execute()

                # Simulate work
                duration = random.uniform(*self.duration_range)
                await asyncio.sleep(duration)
                
                # Add operation attributes
                self._add_operation_attributes(span)
                
                # Handle success/failure
                if random.random() < self._get_success_rate():
                    self._handle_success(span)
                else:
                    self._handle_failure(span)

            except Exception as e:
                span.record_exception(e)
                raise

    def _add_operation_attributes(self, span: trace.Span) -> None:
        """Add operation-specific attributes to the span."""
        attrs = {
            "database": {
                "db.system": "postgresql",
                "db.operation": random.choice(["SELECT", "INSERT", "UPDATE", "DELETE"]),
                "db.name": "products_db"
            },
            "http": {
                "http.method": random.choice(["GET", "POST", "PUT", "DELETE"]),
                "http.url": f"https://api.example.com/v1/{self.name}",
                "http.status_code": random.choice([200, 201, 400, 500])
            },
            "queue": {
                "messaging.system": "rabbitmq",
                "messaging.operation": random.choice(["send", "receive"]),
                "messaging.destination": f"queue.{self.name}"
            },
            "cache": {
                "cache.operation": random.choice(["get", "set", "delete"]),
                "cache.system": "redis"
            }
        }
        
        if self.operation_type in attrs:
            for key, value in attrs[self.operation_type].items():
                span.set_attribute(key, value)

    def _get_success_rate(self) -> float:
        """Get success rate based on operation type."""
        rates = {
            "database": 0.95,
            "http": 0.85,
            "queue": 0.90,
            "cache": 0.98,
            "processing": 0.92,
            "validation": 0.88,
            "transformation": 0.93,
            "export": 0.94
        }
        return rates.get(self.operation_type, 0.9)

    def _handle_success(self, span: trace.Span) -> None:
        """Handle successful execution."""
        self.status = "completed"
        span.set_status(Status(StatusCode.OK))
        span.set_attribute("step.status", "completed")

    def _handle_failure(self, span: trace.Span) -> None:
        """Handle execution failure."""
        error_messages = {
            "database": [
                "Database connection timeout",
                "Deadlock detected",
                "Unique constraint violation"
            ],
            "http": [
                "API rate limit exceeded",
                "External service unavailable",
                "Invalid response format"
            ],
            "queue": [
                "Queue full",
                "Message processing timeout",
                "Consumer disconnected"
            ],
            "cache": [
                "Cache eviction",
                "Key not found",
                "Cache server unreachable"
            ]
        }

        error_msg = random.choice(
            error_messages.get(
                self.operation_type,
                [f"{self.operation_type.title()} operation failed"]
            )
        )
        
        self.status = "failed"
        self.error = error_msg
        span.set_status(Status(StatusCode.ERROR))
        span.set_attribute("step.status", "failed")
        span.set_attribute("step.error", error_msg)
        raise Exception(error_msg)


class WorkflowSimulator:
    """Workflow simulator that executes multiple steps with OpenTelemetry instrumentation."""

    def __init__(self, name: str):
        self.name = name
        self.steps: List[Step] = []
        self.status: Optional[str] = None
        self.error: Optional[str] = None

    def add_step(self, step: Step) -> None:
        """Add a step to the workflow."""
        self.steps.append(step)

    async def execute(self) -> None:
        """Execute the workflow with tracing."""
        with tracer.start_as_current_span(
            f"workflow.{self.name}",
            attributes={
                "workflow.name": self.name,
                "workflow.type": "simulation"
            },
        ) as span:
            try:
                for step in self.steps:
                    await step.execute()
                self.status = "completed"
                span.set_status(Status(StatusCode.OK))
                span.set_attribute("workflow.status", "completed")
            except Exception as e:
                self.status = "failed"
                self.error = str(e)
                span.set_status(Status(StatusCode.ERROR))
                span.set_attribute("workflow.status", "failed")
                span.set_attribute("workflow.error", self.error)
                span.record_exception(e)
                raise 


# Workflow helper functions

def create_step_from_config(config: StepConfig) -> Step:
    """Create a Step from a StepConfig."""
    try:
        return Step(
            name=config.name,
            operation_type=config.operation_type.value,
            duration_range=config.duration_range,
            parallel=config.parallel,
            substeps=[create_step_from_config(substep) for substep in config.substeps],
            attributes=config.attributes
        )
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Invalid operation type: {config.operation_type}",
                "valid_types": [op.value for op in OperationType]
            }
        )


def create_default_workflow() -> list[Step]:
    """Create the default complex workflow steps with OpenTelemetry instrumentation."""
    return [
        Step(
            "data_ingestion",
            OperationType.PROCESSING.value,
            parallel=True,
            substeps=[
                Step("read_database", OperationType.DATABASE.value, (0.2, 0.4)),
                Step("fetch_api_data", OperationType.HTTP.value, (0.3, 0.6)),
                Step("read_queue", OperationType.QUEUE.value, (0.1, 0.3))
            ]
        ),
        Step(
            "data_processing",
            OperationType.PROCESSING.value,
            substeps=[
                Step("validate_data", OperationType.VALIDATION.value, (0.1, 0.2)),
                Step("transform_data", OperationType.TRANSFORMATION.value, (0.2, 0.3))
            ]
        ),
        Step(
            "data_storage",
            OperationType.PROCESSING.value,
            parallel=True,
            substeps=[
                Step("cache_results", OperationType.CACHE.value, (0.1, 0.2)),
                Step("save_to_database", OperationType.DATABASE.value, (0.2, 0.4)),
                Step("publish_event", OperationType.QUEUE.value, (0.1, 0.3))
            ]
        )
    ]


async def execute_workflow(name: str, steps=None) -> WorkflowSimulator:
    """Execute a workflow with OpenTelemetry instrumentation."""
    workflow = WorkflowSimulator(name)
    
    # Use custom steps if provided, otherwise use default workflow
    workflow_steps = (
        [create_step_from_config(step) for step in steps]
        if steps
        else create_default_workflow()
    )
    
    # Add steps to workflow
    for step in workflow_steps:
        workflow.add_step(step)
    
    await workflow.execute()
    return workflow 