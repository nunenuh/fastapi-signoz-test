# Workflow Simulator Package

This package contains workflow simulators with different levels of complexity and instrumentation:

## Structure

- **simple.py**: Simple workflow simulator without OpenTelemetry instrumentation
- **medium.py**: Medium complexity workflow with detailed execution tracking
- **complex.py**: Complex workflow with full OpenTelemetry instrumentation

## Components

### Simple Workflow

- Basic implementation with minimal features
- No telemetry instrumentation
- Simple linear execution flow
- Used to demonstrate baseline performance

### Medium Workflow

- Intermediate complexity with detailed execution tracking
- No explicit OpenTelemetry instrumentation
- More detailed operations and nested steps
- Captures timing and execution details

### Complex Workflow

- Advanced implementation with full OpenTelemetry instrumentation
- Detailed span creation and attribute tracking
- Hierarchical span relationships
- Complete telemetry for all operations

## Usage

Import the components you need from the package:

```python
# Import specific simulators
from fastapi_signoz_test.simulate.simulator import (
    SimpleStep, SimpleWorkflowSimulator, execute_simple_workflow,
    MediumStep, MediumWorkflowSimulator, execute_medium_workflow,
    Step, WorkflowSimulator, execute_workflow
)

# Or use the helper functions directly
from fastapi_signoz_test.simulate.simulator import execute_workflow
```

## API Endpoints

The application provides four main endpoints:

- `POST /workflow/simple`: Basic workflow without telemetry
- `POST /workflow/medium`: Medium complexity workflow with detailed execution tracking
- `POST /workflow/complex`: Complex workflow with full OpenTelemetry tracing
- `POST /workflow/error`: Error demonstration endpoint

All endpoints accept POST requests with an optional JSON body. If no body is provided, they will run the default workflow configuration. 