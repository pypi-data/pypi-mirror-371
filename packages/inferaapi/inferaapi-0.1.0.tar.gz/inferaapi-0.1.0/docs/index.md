# inferaAPI Documentation

inferaAPI is a unified REST API framework for multiple LLM providers, designed for research and development.

## Features

- Support for multiple LLM providers (OpenAI, Anthropic, HuggingFace, custom)
- RESTful API with Swagger/OpenAPI documentation
- Streaming responses via Server-Sent Events and WebSockets
- Batch processing and model comparison
- Custom model registration
- Rate limiting and authentication

## Quick Start

1. Install the package:


pip install inferaapi

2. Set up environment variables:

export OPENAI_API_KEY=your_key
export ANTHROPIC_API_KEY=your_key

3. Run the server:

inferaapi

4. Visit http://localhost:8000/api/docs for API documentation

    # API Endpoints
    - POST /api/generate - Generate text
    - POST /api/stream - Stream text generation
    - POST /api/batch - Process multiple prompts
    - POST /api/compare - Compare different models
    - GET /api/models - List available models
    - POST /api/models/register - Register custom models
    - GET /api/health - Check API health
    - WS /api/ws - WebSocket for streaming

    