"""Medium complexity simulator module."""

import asyncio
import random
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import HTTPException, status

from ..schemas import StepConfig, OperationType


class MediumStep:
    """Medium complexity step class with execution details."""

    def __init__(
        self,
        name: str,
        operation_type: str,
        duration_range: tuple[float, float] = (0.1, 0.5),
        parallel: bool = False,
        substeps: Optional[List['MediumStep']] = None,
        attributes: Optional[Dict[str, Any]] = None,
        success_rate: Optional[float] = None
    ):
        self.name = name
        self.operation_type = operation_type
        self.duration_range = duration_range
        self.parallel = parallel
        self.substeps = substeps or []
        self.attributes = attributes or {}
        self.status: Optional[str] = None
        self.error: Optional[str] = None
        # Additional execution details
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.duration: Optional[float] = None
        # Custom success rate if provided
        self.success_rate = success_rate

    async def execute(self) -> None:
        """Execute the step with timing information."""
        self.start_time = datetime.now()
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
            self.duration = duration
            
            # For the test endpoints, increase success rate to 0.95 for all operations
            # to make demos more reliable
            if random.random() < (self.success_rate or self._get_success_rate()):
                self._handle_success()
            else:
                self._handle_failure()

        except Exception as e:
            self.status = "failed"
            self.error = str(e)
            raise
        finally:
            self.end_time = datetime.now()

    def _get_success_rate(self) -> float:
        """Get success rate based on operation type."""
        # Higher success rates for more reliable demo
        rates = {
            "database": 0.98,
            "http": 0.97,
            "queue": 0.97,
            "cache": 0.99,
            "processing": 0.98,
            "validation": 0.98,
            "transformation": 0.97,
            "export": 0.97
        }
        return rates.get(self.operation_type, 0.98)

    def _handle_success(self) -> None:
        """Handle successful execution with operation details."""
        self.status = "completed"
        # Convert to string to ensure JSON serialization works
        self.attributes["duration"] = str(self.duration)
        self.attributes["operation_success"] = "true"

    def _handle_failure(self) -> None:
        """Handle execution failure with detailed error information."""
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
        # Convert to string to ensure JSON serialization works
        self.attributes["error_type"] = self.operation_type
        self.attributes["error_message"] = error_msg
        self.attributes["operation_success"] = "false"
        raise Exception(error_msg)


class MediumWorkflowSimulator:
    """Medium complexity workflow simulator with detailed execution tracking."""

    def __init__(self, name: str):
        self.name = name
        self.steps: List[MediumStep] = []
        self.status: Optional[str] = None
        self.error: Optional[str] = None
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.execution_details: Dict[str, Any] = {}

    def add_step(self, step: MediumStep) -> None:
        """Add a step to the workflow."""
        self.steps.append(step)

    async def execute(self) -> None:
        """Execute the workflow with detailed tracking."""
        self.start_time = datetime.now()
        try:
            for step in self.steps:
                try:
                    await step.execute()
                    # Collect execution details - ensure JSON serializable
                    self.execution_details[step.name] = {
                        "status": step.status,
                        "duration": str(step.duration) if step.duration is not None else None,
                        "start_time": step.start_time.isoformat() if step.start_time else None,
                        "end_time": step.end_time.isoformat() if step.end_time else None
                    }
                except Exception as e:
                    # Mark the workflow as failed but continue processing for demo purposes
                    self.status = "failed"
                    self.error = str(e)
                    self.execution_details[step.name] = {
                        "status": "failed",
                        "error": str(e),
                        "duration": str(step.duration) if step.duration is not None else None,
                        "start_time": step.start_time.isoformat() if step.start_time else None,
                        "end_time": step.end_time.isoformat() if step.end_time else None
                    }
                    
            # If status is still None, set it to completed (no failures occurred)
            if self.status is None:
                self.status = "completed"
                
        except Exception as e:
            # This should rarely happen with the above error handling
            self.status = "failed"
            self.error = str(e)
        finally:
            self.end_time = datetime.now()
            if self.start_time and self.end_time:
                total_duration = (self.end_time - self.start_time).total_seconds()
                self.execution_details["total_duration"] = str(total_duration)


# Workflow helper functions

def create_medium_step_from_config(config: StepConfig) -> MediumStep:
    """Create a MediumStep from a StepConfig."""
    try:
        return MediumStep(
            name=config.name,
            operation_type=config.operation_type.value,
            duration_range=config.duration_range,
            parallel=config.parallel,
            substeps=[create_medium_step_from_config(substep) for substep in config.substeps],
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


def create_medium_default_workflow() -> list[MediumStep]:
    """Create the default medium complexity workflow steps.
    
    A medium complexity workflow that demonstrates:
    1. Initial data gathering from multiple sources
    2. Data processing with validation and transformation
    3. Multiple storage operations
    4. Basic error handling
    """
    return [
        # Stage 1: Multi-source data gathering
        MediumStep(
            "data_gathering",
            OperationType.PROCESSING.value,
            parallel=True,
            substeps=[
                # Database operations
                MediumStep(
                    "database_ops",
                    OperationType.PROCESSING.value,
                    parallel=True,
                    substeps=[
                        MediumStep("read_users", OperationType.DATABASE.value, (0.1, 0.2), success_rate=0.99),
                        MediumStep("read_orders", OperationType.DATABASE.value, (0.1, 0.3), success_rate=0.99)
                    ],
                    success_rate=0.99
                ),
                # External API calls
                MediumStep(
                    "api_ops",
                    OperationType.PROCESSING.value,
                    parallel=True,
                    substeps=[
                        MediumStep("fetch_inventory", OperationType.HTTP.value, (0.1, 0.2), success_rate=0.99),
                        MediumStep("fetch_pricing", OperationType.HTTP.value, (0.1, 0.2), success_rate=0.99)
                    ],
                    success_rate=0.99
                )
            ],
            success_rate=0.99
        ),
        
        # Stage 2: Data processing pipeline
        MediumStep(
            "processing_pipeline",
            OperationType.PROCESSING.value,
            substeps=[
                # Validation stage
                MediumStep(
                    "validation",
                    OperationType.VALIDATION.value,
                    substeps=[
                        MediumStep("validate_data", OperationType.VALIDATION.value, (0.1, 0.2), success_rate=0.99)
                    ],
                    success_rate=0.99
                ),
                # Transformation stage
                MediumStep(
                    "transformation",
                    OperationType.TRANSFORMATION.value,
                    substeps=[
                        MediumStep("transform_data", OperationType.TRANSFORMATION.value, (0.1, 0.2), success_rate=0.99)
                    ],
                    success_rate=0.99
                )
            ],
            success_rate=0.99
        ),
        
        # Stage 3: Storage operations
        MediumStep(
            "storage_ops",
            OperationType.PROCESSING.value,
            substeps=[
                # Cache the processed data
                MediumStep("update_cache", OperationType.CACHE.value, (0.1, 0.2), success_rate=0.99),
                # Store the results
                MediumStep("save_to_db", OperationType.DATABASE.value, (0.1, 0.2), success_rate=0.99)
            ],
            success_rate=0.99
        )
    ]


async def execute_medium_workflow(name: str, steps=None) -> MediumWorkflowSimulator:
    """Execute a medium complexity workflow."""
    workflow = MediumWorkflowSimulator(name)
    
    # Use custom steps if provided, otherwise use default workflow
    try:
        workflow_steps = (
            [create_medium_step_from_config(step) for step in steps]
            if steps
            else create_medium_default_workflow()
        )
        
        # Add steps to workflow
        for step in workflow_steps:
            workflow.add_step(step)
        
        await workflow.execute()
    except Exception as e:
        # Ensure the workflow has a status and error message even if setup fails
        workflow.status = "failed"
        workflow.error = f"Workflow initialization failed: {str(e)}"
    
    return workflow 