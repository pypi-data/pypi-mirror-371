# Coalex SDK

A Python package for OpenTelemetry integration with Coalex.ai observability platform.

## Installation

```bash
pip install coalex
```

## Quick Start with VertexAI

```python
from coalex.otel import register, add_request_context
from openinference.instrumentation.vertexai import VertexAIInstrumentor
from vertexai.generative_models import GenerativeModel

# Register Coalex tracing
tracer_provider = register(
    agent_id="YOUR_AGENT_ID"
)

# Instrument VertexAI with Coalex tracer
VertexAIInstrumentor().instrument(tracer_provider=tracer_provider)

# Create model instance
model = GenerativeModel("gemini-2.0-flash")

# Add request context for this interaction
add_request_context(
    request_id="req_vertex_001",
    prompt_version="v1.0.0"
)

# Generate content - this will be automatically traced
response = model.generate_content(
    "Write a haiku about artificial intelligence.",
    generation_config={
        "max_output_tokens": 100,
        "temperature": 0.7,
    }
)

print("Generated haiku:")
print(response.text)
```

## Features

- **Simple Setup**: One-line registration with `register()`
- **Coalex Integration**: Default endpoint for Coalex observability platform
- **Request Context**: Easy addition of request_id and prompt_version
- **OpenInference Compatible**: Works with all OpenInference instrumentors
- **Authentication**: Automatic authentication using agent_id

## Configuration

- `agent_id`: Your unique agent identifier (required for authentication)
- `endpoint`: OTLP endpoint (defaults to Coalex: `https://traces.coalex.ai/v1/traces`)
- `service_name`: Name of the service (default: "coalex-service")

## Example

See `examples/vertexai_example.py` for a complete working example including:

- Basic content generation
- Streaming responses
- Proper error handling
- Request context management

To run the example, install the additional dependencies:
```bash
pip install google-cloud-aiplatform openinference-instrumentation-vertexai
```

