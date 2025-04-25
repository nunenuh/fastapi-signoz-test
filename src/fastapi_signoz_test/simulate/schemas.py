"""Schema definitions for the simulation module."""

from enum import Enum
from typing import List, Optional, Dict, Any, Tuple

from pydantic import BaseModel, Field


class OperationType(str, Enum):
    """Valid operation types for workflow steps."""
    DATABASE = "database"
    HTTP = "http"
    QUEUE = "queue"
    CACHE = "cache"
    PROCESSING = "processing"
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"
    EXPORT = "export"


class StepConfig(BaseModel):
    """Configuration for a workflow step."""
    name: str = Field(
        ..., 
        description="Name of the step",
        example="fetch_data"
    )
    operation_type: OperationType = Field(
        ...,
        description="Type of operation to perform"
    )
    duration_range: Tuple[float, float] = Field(
        default=(0.1, 0.5),
        description="Tuple of (min_duration, max_duration) in seconds"
    )
    parallel: bool = Field(
        default=False,
        description="Whether substeps should be executed in parallel"
    )
    substeps: List["StepConfig"] = Field(
        default_factory=list,
        description="List of substeps to execute"
    )
    attributes: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional attributes to add to the span"
    )


class WorkflowRequest(BaseModel):
    """Request model for creating a workflow."""
    name: str = Field(
        ..., 
        description="Name of the workflow",
        example="data_pipeline"
    )
    steps: Optional[List[StepConfig]] = Field(
        default=None,
        description="Optional custom steps. If not provided, default workflow will be used"
    )

    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "name": "data_pipeline",
                "steps": [
                    {
                        "name": "fetch_data",
                        "operation_type": "http",
                        "duration_range": [0.2, 0.4],
                        "parallel": True,
                        "substeps": [
                            {
                                "name": "fetch_users",
                                "operation_type": "http",
                                "duration_range": [0.1, 0.3]
                            },
                            {
                                "name": "fetch_orders",
                                "operation_type": "database",
                                "duration_range": [0.2, 0.4]
                            }
                        ]
                    }
                ]
            }
        }


class WorkflowResponse(BaseModel):
    """Response model for workflow execution."""
    status: str = Field(
        ...,
        description="Status of the workflow execution",
        example="completed"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if workflow failed"
    )

    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "status": "completed",
                "error": None
            }
        }


# Required for recursive Pydantic models
StepConfig.model_rebuild()

# Example requests for documentation
SIMPLE_WORKFLOW_EXAMPLE = {
    "name": "simple_workflow"
}

MEDIUM_WORKFLOW_EXAMPLE = {
    "name": "medium_workflow",
    "steps": [
        {
            "name": "data_gathering",
            "operation_type": "processing",
            "parallel": True,
            "substeps": [
                {
                    "name": "database_ops",
                    "operation_type": "processing",
                    "parallel": True,
                    "substeps": [
                        {
                            "name": "read_users",
                            "operation_type": "database",
                            "duration_range": [0.2, 0.4]
                        },
                        {
                            "name": "read_orders",
                            "operation_type": "database",
                            "duration_range": [0.3, 0.5]
                        }
                    ]
                },
                {
                    "name": "api_ops",
                    "operation_type": "processing",
                    "parallel": True,
                    "substeps": [
                        {
                            "name": "fetch_inventory",
                            "operation_type": "http",
                            "duration_range": [0.2, 0.4]
                        },
                        {
                            "name": "fetch_pricing",
                            "operation_type": "http",
                            "duration_range": [0.1, 0.3]
                        }
                    ]
                }
            ]
        }
    ]
}

COMPLEX_WORKFLOW_EXAMPLE = WorkflowRequest.Config.schema_extra["example"]

ERROR_RESPONSE_EXAMPLE = {
    "detail": {
        "message": "Invalid operation type: unknown",
        "valid_types": [op.value for op in OperationType]
    }
}

FAILURE_RESPONSE_EXAMPLE = {
    "detail": {
        "message": "Workflow execution failed",
        "error": "Database connection timeout"
    }
}

__all__ = [
    "OperationType",
    "StepConfig",
    "WorkflowRequest",
    "WorkflowResponse",
    "SIMPLE_WORKFLOW_EXAMPLE",
    "MEDIUM_WORKFLOW_EXAMPLE",
    "COMPLEX_WORKFLOW_EXAMPLE",
    "ERROR_RESPONSE_EXAMPLE",
    "FAILURE_RESPONSE_EXAMPLE"
]
