from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Route

from ..config import settings


class OpenAPIEndpoint(HTTPEndpoint):
    async def get(self, request: Request):
        openapi_schema = {
            "openapi": "3.0.0",
            "info": {
                "title": settings.app_name,
                "version": settings.app_version,
                "description": settings.description,
                "contact": {
                    "name": "API Support",
                    "url": "https://github.com/yourusername/inferaapi/issues",
                },
            },
            "servers": [
                {
                    "url": f"http://{settings.host}:{settings.port}",
                    "description": "Development server",
                }
            ],
            "paths": {
                "/api/generate": {
                    "post": {
                        "summary": "Generate text from a prompt",
                        "description": "Generate text using the specified LLM" "provider and model",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/LLMRequest"}
                                }
                            },
                        },
                        "responses": {
                            "200": {
                                "description": "Successful response",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/LLMResponse"}
                                    }
                                },
                            },
                            "400": {
                                "description": "Bad request",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                                    }
                                },
                            },
                            "404": {
                                "description": "Model not found",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                                    }
                                },
                            },
                        },
                    }
                },
                "/api/stream": {
                    "post": {
                        "summary": "Stream generated text",
                        "description": "Stream text generation using Server-Sent" "Events",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/LLMRequest"}
                                }
                            },
                        },
                        "responses": {
                            "200": {
                                "description": "Successful stream",
                                "content": {
                                    "text/event-stream": {
                                        "schema": {"type": "string", "format": "binary"}
                                    }
                                },
                            }
                        },
                    }
                },
                # Add documentation for other endpoints...
            },
            "components": {
                "schemas": {
                    "LLMRequest": {
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string"},
                            "max_tokens": {"type": "integer", "default": 100},
                            "temperature": {"type": "number", "default": 0.7},
                            "top_p": {"type": "number", "default": 1.0},
                            "stop_sequences": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "stream": {"type": "boolean", "default": False},
                            "model": {"type": "string"},
                            "provider": {"type": "string"},
                        },
                        "required": ["prompt", "provider"],
                    },
                    "LLMResponse": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string"},
                            "model": {"type": "string"},
                            "provider": {"type": "string"},
                            "tokens_used": {"type": "integer"},
                            "finish_reason": {"type": "string"},
                            "processing_time": {"type": "number"},
                            "metadata": {"type": "object"},
                        },
                    },
                    "ErrorResponse": {
                        "type": "object",
                        "properties": {
                            "error": {"type": "string"},
                            "code": {"type": "integer"},
                            "details": {"type": "object"},
                        },
                    },
                },
                "securitySchemes": {"BearerAuth": {"type": "http", "scheme": "bearer"}},
            },
        }

        return JSONResponse(openapi_schema)


class SwaggerUIEndpoint(HTTPEndpoint):
    async def get(self, request: Request):
        swagger_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>{settings.app_name} - Swagger UI</title>
            "  <link rel=\"stylesheet\" type=\"text/css\"\n"
            "  href=\"https://unpkg.com/swagger-ui-dist@3.25.0/"
        </head>
        <body>
            <div id="swagger-ui"></div>
            "  <script src=\"https://unpkg.com/swagger-ui-dist@3.25.0/"
            "swagger-ui-bundle.js\"></script>\n"
            "  <script>\n"
            <script>
                SwaggerUIBundle({{
                    url: '/api/openapi.json',
                    dom_id: '#swagger-ui',
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIBundle.presets.standalone
                    ],
                    layout: "BaseLayout"
                }})
            </script>
        </body>
        </html>
        """
        return HTMLResponse(swagger_html)


# Documentation routes
docs_routes = [
    Route("/openapi.json", OpenAPIEndpoint),
    Route("/docs", SwaggerUIEndpoint),
    Route("/swagger", SwaggerUIEndpoint),
]
