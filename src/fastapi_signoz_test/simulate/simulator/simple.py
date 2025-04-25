"""Simple simulator module without telemetry."""

import asyncio
import random
from typing import List, Optional, Dict, Any

from fastapi import HTTPException, status

from ..schemas import StepConfig, OperationType


class SimpleStep:
    """Simple step class without telemetry."""

    def __init__(
        self,
        name: str,
        operation_type: str,
        duration_range: tuple[float, float] = (0.1, 0.5),
        parallel: bool = False,
        substeps: Optional[List['SimpleStep']] = None,
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
        """Execute the step without telemetry."""
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
            
            # Simulate success/failure
            if random.random() < self._get_success_rate():
                self._handle_success()
            else:
                self._handle_failure()

        except Exception as e:
            self.status = "failed"
            self.error = str(e)
            raise

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

    def _handle_success(self) -> None:
        """Handle successful execution."""
        self.status = "completed"

    def _handle_failure(self) -> None:
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
        raise Exception(error_msg)


class SimpleWorkflowSimulator:
    """Simple workflow simulator without telemetry."""

    def __init__(self, name: str):
        self.name = name
        self.steps: List[SimpleStep] = []
        self.status: Optional[str] = None
        self.error: Optional[str] = None

    def add_step(self, step: SimpleStep) -> None:
        """Add a step to the workflow."""
        self.steps.append(step)

    async def execute(self) -> None:
        """Execute the workflow without telemetry."""
        try:
            for step in self.steps:
                await step.execute()
            self.status = "completed"
        except Exception as e:
            self.status = "failed"
            self.error = str(e)
            raise


# Workflow helper functions

def create_simple_step_from_config(config: StepConfig) -> SimpleStep:
    """Create a SimpleStep from a StepConfig."""
    try:
        return SimpleStep(
            name=config.name,
            operation_type=config.operation_type.value,
            duration_range=config.duration_range,
            parallel=config.parallel,
            substeps=[create_simple_step_from_config(substep) for substep in config.substeps],
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


def create_simple_default_workflow() -> list[SimpleStep]:
    """Create the default simple workflow steps.
    
    A simple linear workflow that:
    1. Fetches data from DB and API in parallel
    2. Validates the data
    3. Saves to cache
    """
    return [
        # Step 1: Parallel data fetching
        SimpleStep(
            "data_fetching",
            OperationType.PROCESSING.value,
            parallel=True,
            substeps=[
                SimpleStep("fetch_db_data", OperationType.DATABASE.value, (0.2, 0.4)),
                SimpleStep("fetch_api_data", OperationType.HTTP.value, (0.3, 0.5))
            ]
        ),
        # Step 2: Validation
        SimpleStep(
            "validate_data",
            OperationType.VALIDATION.value,
            duration_range=(0.1, 0.2)
        ),
        # Step 3: Cache
        SimpleStep(
            "save_to_cache",
            OperationType.CACHE.value,
            duration_range=(0.1, 0.3)
        )
    ]


async def execute_simple_workflow(name: str, steps=None) -> SimpleWorkflowSimulator:
    """Execute a simple workflow without telemetry."""
    workflow = SimpleWorkflowSimulator(name)
    
    # Use custom steps if provided, otherwise use default workflow
    workflow_steps = (
        [create_simple_step_from_config(step) for step in steps]
        if steps
        else create_simple_default_workflow()
    )
    
    # Add steps to workflow
    for step in workflow_steps:
        workflow.add_step(step)
    
    await workflow.execute()
    return workflow 