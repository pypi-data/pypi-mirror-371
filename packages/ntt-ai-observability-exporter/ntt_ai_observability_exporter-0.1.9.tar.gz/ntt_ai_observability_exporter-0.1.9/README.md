# NTT AI Observability Exporter
A specialized telemetry exporter for NTT AI Foundry projects using Azure Monitor OpenTelemetry. This package simplifies telemetry setup for AI applications built with Azure services.

## Features

- Automatic instrumentation of Azure SDK libraries
- Simplified configuration for Azure Monitor OpenTelemetry
- Specialized support for Semantic Kernel telemetry
- Compatible with Azure AI Foundry projects

## Installation

```bash
# Using pip
pip install ntt-ai-observability-exporter

# Using uv
uv pip install ntt-ai-observability-exporter
```
## Updating Your Package Documentation

Make sure to add a note in your package documentation (such as README.md) about the dependencies:

```markdown
## Dependencies

This package depends on:
- azure-monitor-opentelemetry (>=1.0.0)
- opentelemetry-sdk (>=1.15.0)

These dependencies will be automatically installed when you install the package via pip.

```bash
# Using pip
pip install ntt-ai-observability-exporter

# Using uv
uv pip install ntt-ai-observability-exporter
```

## Usage

### Simple Usage - One Line Setup

```python
from ntt_ai_observability_exporter import configure_telemetry

# That's it! This single line configures all telemetry
configure_telemetry()

# Now you can use your AI components normally - telemetry is automatic
```

### Configuration Options

```python
# Explicit configuration
configure_telemetry(
    connection_string="InstrumentationKey=your-key;IngestionEndpoint=your-endpoint",
    customer_name="your-customer",
    agent_name="your-agent"
)

```

## What Gets Instrumented Automatically

The Azure Monitor OpenTelemetry package automatically instruments:

- **Azure SDK libraries** (including azure.ai.openai)
- **HTTP client libraries** (requests, aiohttp)

This means when you use Azure AI Foundry components, telemetry is captured without any additional code.

## Configuration Parameters

- `connection_string`: Azure Monitor connection string
- `customer_name`: Maps to `service.name` in OpenTelemetry resource
- `agent_name`: Maps to `service.instance.id` in OpenTelemetry resource

## Environment Variables

You can set these environment variables:

- `AZURE_MONITOR_CONNECTION_STRING`: The connection string for Azure Monitor
- `CUSTOMER_NAME`: Maps to `service.name` in OpenTelemetry resource
- `AGENT_NAME`: Maps to `service.instance.id` in OpenTelemetry resource



## Telemetry Types Captured

The configuration captures:

- **Traces**: Request flows and operations
- **Metrics**: Performance measurements 
- **Logs**: When integrated with Python logging

## Example in Azure AI Foundry Project

```python
# Import the NTT AI Observability Exporter
from ntt_ai_observability_exporter import configure_telemetry

# Configure telemetry with your project details
configure_telemetry(
    connection_string="InstrumentationKey=xxx;IngestionEndpoint=https://westeurope-5.in.applicationinsights.azure.com/",
    customer_name="customer-name-foundry",
    agent_name="ai-foundry-agent"
)

# Now use Azure AI components as normal - telemetry is automatic
from azure.ai.assistant import AssistantClient

client = AssistantClient(...)
# All operations are automatically instrumented
```


## Semantic Kernel Telemetry Support

For applications using Semantic Kernel, use the specialized configuration function:

```python
from ntt_ai_observability_exporter import configure_semantic_kernel_telemetry

# Configure Semantic Kernel telemetry BEFORE creating any Kernel instances
configure_semantic_kernel_telemetry(
    connection_string="your_connection_string",
    customer_name="your_customer_name",
    agent_name="your_agent_name"
)

# Then create and use your Semantic Kernel
from semantic_kernel import Kernel
kernel = Kernel()
# ... rest of your code
```

## Development and Testing

### Installation for Development

Install the package with development dependencies:

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Or install with just testing dependencies
pip install -e ".[test]"

# Or install from requirements-dev.txt
pip install -r requirements-dev.txt
```

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src/ntt_ai_observability_exporter

# Run tests with detailed coverage report
pytest --cov=src/ntt_ai_observability_exporter --cov-report=term-missing

# Run specific test file
pytest tests/test_semantic_kernel_telemetry.py -v
```

### Test Coverage

The package includes comprehensive unit tests with:
- **93% overall test coverage**
- **100% coverage** for semantic kernel telemetry module
- **17 test cases** covering all functionality
- Validation of configuration, error handling, and Azure Monitor integration

### Code Quality

The project uses:
- **pytest** for testing framework
- **black** for code formatting
- **flake8** for linting
- **mypy** for type checking
- **isort** for import sorting
