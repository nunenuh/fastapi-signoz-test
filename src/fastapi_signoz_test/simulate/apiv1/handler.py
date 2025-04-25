"""API endpoints handler module."""

from fastapi import APIRouter, HTTPException, status, Body
import logging

from ...simulate.schemas import (
    WorkflowResponse,
    ERROR_RESPONSE_EXAMPLE,
    FAILURE_RESPONSE_EXAMPLE
)
from ...simulate.simulator import (
    execute_workflow,
    execute_simple_workflow,
    execute_medium_workflow
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/workflow/simple",
    response_model=WorkflowResponse,
    status_code=status.HTTP_200_OK,
    tags=["simulate"],
    responses={
        200: {"model": WorkflowResponse},
        400: {"content": {"application/json": {"example": ERROR_RESPONSE_EXAMPLE}}},
        500: {"content": {"application/json": {"example": FAILURE_RESPONSE_EXAMPLE}}}
    }
)
async def create_and_execute_simple_workflow(
    request: dict = Body(default=None)
) -> WorkflowResponse:
    """Create and execute a simple workflow without OpenTelemetry.
    
    This endpoint demonstrates basic workflow functionality without telemetry.
    Use POST without a body to run the default simple workflow.
    """
    try:
        # If no body provided, use default
        if not request:
            workflow_name = "simple_workflow"
            workflow_steps = None
        else:
            workflow_name = request.get("name", "simple_workflow")
            workflow_steps = request.get("steps")
            
        logger.info(f"Executing simple workflow: {workflow_name}")
        workflow = await execute_simple_workflow(workflow_name, workflow_steps)
        return WorkflowResponse(status=workflow.status)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Simple workflow execution failed", "error": str(e)},
        )


@router.post(
    "/workflow/medium",
    response_model=WorkflowResponse,
    status_code=status.HTTP_200_OK,
    tags=["simulate"],
    responses={
        200: {"model": WorkflowResponse},
        400: {"content": {"application/json": {"example": ERROR_RESPONSE_EXAMPLE}}},
        500: {"content": {"application/json": {"example": FAILURE_RESPONSE_EXAMPLE}}}
    }
)
async def create_and_execute_medium_workflow(
    request: dict = Body(default=None)
) -> WorkflowResponse:
    """Create and execute a medium complexity workflow without OpenTelemetry.
    
    This endpoint demonstrates a more complex workflow with multiple stages:
    1. Multi-source data gathering (DB, API, Queue)
    2. Parallel processing and validation
    3. Data transformation
    4. Multiple storage operations
    
    Use POST without a body to run the default medium workflow.
    """
    try:
        # If no body provided, use default
        if not request:
            workflow_name = "medium_workflow"
            workflow_steps = None
        else:
            workflow_name = request.get("name", "medium_workflow")
            workflow_steps = request.get("steps")
        
        logger.info(f"Executing medium workflow: {workflow_name}")
        workflow = await execute_medium_workflow(workflow_name, workflow_steps)
        logger.info(f"Medium workflow completed with status: {workflow.status}")
        
        # Create a clean response with just the required fields
        response = WorkflowResponse(
            status=workflow.status,
            error=workflow.error
        )
        return response
    except HTTPException:
        logger.error("Medium workflow HTTP exception", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Medium workflow execution failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Medium workflow execution failed", "error": str(e)},
        )


@router.post(
    "/workflow/complex",
    response_model=WorkflowResponse,
    status_code=status.HTTP_200_OK,
    tags=["simulate"],
    responses={
        200: {"model": WorkflowResponse},
        400: {"content": {"application/json": {"example": ERROR_RESPONSE_EXAMPLE}}},
        500: {"content": {"application/json": {"example": FAILURE_RESPONSE_EXAMPLE}}}
    }
)
async def create_and_execute_complex_workflow(
    request: dict = Body(default=None)
) -> WorkflowResponse:
    """Create and execute a complex workflow with OpenTelemetry.
    
    This endpoint uses OpenTelemetry for tracing and monitoring.
    Use POST without a body to run the default workflow.
    For demonstration purposes, this endpoint always returns a 200 status.
    """
    workflow_name = "complex_workflow"
    workflow_steps = None
    
    if request:
        workflow_name = request.get("name", workflow_name)
        workflow_steps = request.get("steps")
    
    try:
        logger.info(f"Executing complex workflow: {workflow_name}")
        workflow = await execute_workflow(workflow_name, workflow_steps)
        logger.info(f"Complex workflow completed with status: {workflow.status}")
        
        # Always return completed status for demos
        return WorkflowResponse(
            status="completed",
            error=None
        )
    except Exception as e:
        # Log but don't propagate the error
        logger.error(f"Complex workflow error (handled): {str(e)}", exc_info=True)
        return WorkflowResponse(
            status="completed",
            error=f"Error handled for demo: {str(e)}"
        )


@router.post(
    "/workflow/error",
    response_model=WorkflowResponse,
    status_code=status.HTTP_200_OK,
    tags=["simulate"],
    responses={
        200: {"model": WorkflowResponse},
        500: {"content": {"application/json": {"example": FAILURE_RESPONSE_EXAMPLE}}}
    }
)
async def trigger_error_workflow() -> WorkflowResponse:
    """Endpoint that always triggers an error.
    
    This endpoint demonstrates error handling without explicit telemetry.
    It will still be traced by the global tracer if configured.
    """
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "message": "This is a demonstration error endpoint",
            "error": "Intentional error for demonstration purposes"
        }
    )
