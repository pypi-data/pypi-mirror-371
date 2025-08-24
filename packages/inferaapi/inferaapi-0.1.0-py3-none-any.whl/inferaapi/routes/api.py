import asyncio
import json

# Add this at the top with other imports
import logging

from starlette.endpoints import HTTPEndpoint, WebSocketEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse
from starlette.routing import Route, WebSocketRoute

from ..config import settings
from ..exceptions import ModelNotFoundError, ModelRegistrationError, ProviderNotAvailableError
from ..models import model_registry
from ..schemas.requests import (
    BatchLLMRequest,
    ComparisonRequest,
    LLMRequest,
    ModelRegistrationRequest,
)
from ..schemas.responses import (
    BatchLLMResponse,
    ComparisonResponse,
    ErrorResponse,
    HealthResponse,
    ModelsListResponse,
)

logger = logging.getLogger("inferaapi")


class LLMEndpoint(HTTPEndpoint):
    async def post(self, request: Request):
        try:
            # Parse and validate request
            llm_request = LLMRequest(**(await request.json()))
            logger.debug(f"Received request: {llm_request}")

            # Get model instance
            model = await model_registry.get_model(llm_request.provider, llm_request.model)
            logger.debug(f"Using model: {model.model_name}")

            # Convert to internal request format
            internal_request = LLMRequest(
                prompt=llm_request.prompt,
                provider=llm_request.provider,
                max_tokens=llm_request.max_tokens,
                temperature=llm_request.temperature,
                top_p=llm_request.top_p,
                stop_sequences=llm_request.stop_sequences,
                stream=llm_request.stream,
                model=llm_request.model,
            )

            # Generate response
            response = await model.generate(internal_request)
            logger.debug(f"Generated response: {response}")

            return JSONResponse(response.model_dump())

        except (ModelNotFoundError, ProviderNotAvailableError) as e:
            logger.error(f"Model error: {e}")
            return JSONResponse(ErrorResponse(error=str(e), code=404).model_dump(), status_code=404)
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return JSONResponse(ErrorResponse(error=str(e), code=500).model_dump(), status_code=500)


class StreamLLMEndpoint(HTTPEndpoint):
    async def post(self, request: Request):
        try:
            # Parse and validate request
            llm_request = LLMRequest(**(await request.json()))

            # Get model instance
            model = await model_registry.get_model(llm_request.provider, llm_request.model)

            # Convert to internal request format
            # internal_request = LLMRequest(
            #     prompt=llm_request.prompt,
            #     provider=llm_request.provider,
            #     max_tokens=llm_request.max_tokens,
            #     temperature=llm_request.temperature,
            #     top_p=llm_request.top_p,
            #     stop_sequences=llm_request.stop_sequences,
            #     stream=True,
            # )
            # Use model_dump() to create a copy
            request_data = llm_request.model_dump()
            request_data["stream"] = True  # Ensure streaming is enabled
            internal_request = LLMRequest(**request_data)

            # Stream response
            async def generate():
                async for chunk in model.stream_generate(internal_request):
                    yield f"data: {json.dumps(chunk.model_dump())}\n\n"
                yield "data: [DONE]\n\n"

            return StreamingResponse(
                generate(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",  # Disable buffering for nginx
                },
            )

        except (ModelNotFoundError, ProviderNotAvailableError) as e:
            return JSONResponse(ErrorResponse(error=str(e), code=404).model_dump(), status_code=404)
        except Exception as e:
            return JSONResponse(ErrorResponse(error=str(e), code=500).model_dump(), status_code=500)


class BatchLLMEndpoint(HTTPEndpoint):
    async def post(self, request: Request):
        try:
            batch_request = BatchLLMRequest(**(await request.json()))
            responses = []

            for llm_request in batch_request.requests:
                # Get model instance
                model = await model_registry.get_model(llm_request.provider, llm_request.model)

                # Convert to internal request format
                # internal_request = LLMRequest(
                #     prompt=llm_request.prompt,
                #     max_tokens=llm_request.max_tokens,
                #     temperature=llm_request.temperature,
                #     top_p=llm_request.top_p,
                #     stop_sequences=llm_request.stop_sequences,
                #     stream=llm_request.stream,
                # )
                # Use model_dump() to create a copy
                request_data = llm_request.model_dump()
                internal_request = LLMRequest(**request_data)

                # Generate response
                response = await model.generate(internal_request)
                responses.append(response.model_dump())

            return JSONResponse(BatchLLMResponse(responses=responses).model_dump())

        except (ModelNotFoundError, ProviderNotAvailableError) as e:
            return JSONResponse(ErrorResponse(error=str(e), code=404).model_dump(), status_code=404)
        except Exception as e:
            return JSONResponse(ErrorResponse(error=str(e), code=500).model_dump(), status_code=500)


class CompareModelsEndpoint(HTTPEndpoint):
    async def post(self, request: Request):
        try:
            compare_request = ComparisonRequest(**(await request.json()))
            results = {}

            for model_config in compare_request.models:
                provider = model_config["provider"]
                model_name = model_config.get("model")

                # Get model instance
                model = await model_registry.get_model(provider, model_name)

                # Convert to internal request format
                request_data = {
                    "prompt": compare_request.prompt,
                    "provider": provider,
                    "model": model_name,
                    "max_tokens": model_config.get("max_tokens", 100),
                    "temperature": model_config.get("temperature", 0.7),
                    "top_p": model_config.get("top_p", 1.0),
                    "stop_sequences": model_config.get("stop_sequences"),
                    "stream": model_config.get("stream", False),
                }
                internal_request = LLMRequest(**request_data)

                # Generate response
                response = await model.generate(internal_request)

                key = f"{provider}:{model_name}" if model_name else provider
                results[key] = response.model_dump()
            return JSONResponse(
                ComparisonResponse(prompt=compare_request.prompt, results=results).model_dump()
            )
        except (ModelNotFoundError, ProviderNotAvailableError) as e:
            return JSONResponse(ErrorResponse(error=str(e), code=404).model_dump(), status_code=404)
        except Exception as e:
            return JSONResponse(ErrorResponse(error=str(e), code=500).model_dump(), status_code=500)


class ModelsEndpoint(HTTPEndpoint):
    async def get(self, request: Request):
        try:
            # Get the list of models from the registry
            models = model_registry.list_models()

            # Convert to the expected response format
            models_info = {}
            for model_name, model_info in models.items():
                models_info[model_name] = {
                    "name": model_info.get("name", model_name),
                    "provider": model_info.get("provider", "unknown"),
                    "description": model_info.get("description", ""),
                    "max_tokens": model_info.get("max_tokens"),
                    "context_window": model_info.get("context_window"),
                    "capabilities": model_info.get("capabilities", []),
                    "parameters": model_info.get("parameters", {}),
                }

            return JSONResponse(ModelsListResponse(models=models_info).model_dump())

        except Exception as e:
            return JSONResponse(ErrorResponse(error=str(e), code=500).model_dump(), status_code=500)


class RegisterModelEndpoint(HTTPEndpoint):
    async def post(self, request: Request):
        try:
            registration_request = ModelRegistrationRequest(**(await request.json()))

            # In a real implementation, you would securely load the function
            # For this example, we'll just register a simple echo function
            if registration_request.name and registration_request.generate_fn:
                # This is a simplified example - in production you'd need
                # a secure way to register custom functions
                async def custom_generate_fn(prompt, parameters):
                    return f"Echo: {prompt}"

                async def custom_stream_fn(prompt, parameters):
                    for word in prompt.split():
                        yield word + " "
                        await asyncio.sleep(0.1)

                await model_registry.register_custom_model(
                    registration_request.name,
                    custom_generate_fn,
                    custom_stream_fn,
                    registration_request.description or "Custom model",
                )
                return JSONResponse(
                    {
                        "status": "success",
                        "message": (
                            f"Model {registration_request.name} " "registered successfully"
                        ),
                    },
                    status_code=201,
                )
            else:
                return JSONResponse(
                    ErrorResponse(
                        error="Model name and generate function are required", code=400
                    ).model_dump(),
                    status_code=400,
                )

        except ModelRegistrationError as e:
            return JSONResponse(ErrorResponse(error=str(e), code=400).model_dump(), status_code=400)
        except Exception as e:
            return JSONResponse(ErrorResponse(error=str(e), code=500).model_dump(), status_code=500)


class HealthEndpoint(HTTPEndpoint):
    async def get(self, request: Request):
        # Check provider availability
        providers_status = {}
        models_status = {}

        # Check OpenAI
        try:
            await model_registry.get_model("openai", settings.default_openai_model)
            providers_status["openai"] = True
            models_status[settings.default_openai_model] = True
        except Exception:
            providers_status["openai"] = False
            models_status[settings.default_openai_model] = False

        # Check Anthropic
        try:
            await model_registry.get_model("anthropic", settings.default_anthropic_model)
            providers_status["anthropic"] = True
            models_status[settings.default_anthropic_model] = True
        except Exception:
            providers_status["anthropic"] = False
            models_status[settings.default_anthropic_model] = False

        # Check HuggingFace
        try:
            await model_registry.get_model("huggingface", settings.default_huggingface_model)
            providers_status["huggingface"] = True
            models_status[settings.default_huggingface_model] = True
        except Exception:
            providers_status["huggingface"] = False
            models_status[settings.default_huggingface_model] = False

        # Determine overall status
        overall_status = "healthy" if all(providers_status.values()) else "degraded"
        if not any(providers_status.values()):
            overall_status = "unhealthy"

        return JSONResponse(
            HealthResponse(
                status=overall_status,
                providers=providers_status,
                models=models_status,
                version=settings.app_version,
            ).model_dump()
        )


# WebSocket endpoint for streaming
class LLMWebSocketEndpoint(WebSocketEndpoint):
    encoding = "json"

    async def on_receive(self, websocket, data):
        try:
            llm_request = LLMRequest(**data)

            # Get model instance
            model = await model_registry.get_model(llm_request.provider, llm_request.model)

            # Convert to internal request format
            internal_request = LLMRequest(
                prompt=llm_request.prompt,
                max_tokens=llm_request.max_tokens,
                temperature=llm_request.temperature,
                top_p=llm_request.top_p,
                stop_sequences=llm_request.stop_sequences,
                stream=True,
            )

            # Stream response
            async for chunk in model.stream_generate(internal_request):
                await websocket.send_json(chunk.model_dump())

            await websocket.send_json({"status": "complete"})

        except (ModelNotFoundError, ProviderNotAvailableError) as e:
            await websocket.send_json(ErrorResponse(error=str(e), code=404).model_dump())
        except Exception as e:
            await websocket.send_json(ErrorResponse(error=str(e), code=500).model_dump())


# Define routes
routes = [
    Route("/generate", LLMEndpoint),
    Route("/stream", StreamLLMEndpoint),
    Route("/batch", BatchLLMEndpoint),
    Route("/compare", CompareModelsEndpoint),
    Route("/models", ModelsEndpoint),
    Route("/models/register", RegisterModelEndpoint),
    Route("/health", HealthEndpoint),
    WebSocketRoute("/ws", LLMWebSocketEndpoint),
]
