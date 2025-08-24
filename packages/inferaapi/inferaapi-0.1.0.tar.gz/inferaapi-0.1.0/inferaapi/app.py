import logging

import uvicorn
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.responses import RedirectResponse
from starlette.routing import Mount, Route

from .config import settings
from .models import model_registry
from .routes import all_routes

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("inferaapi")


# async def startup():
#     """Initialize the application"""
#     logger.info(f"Starting {settings.app_name} v{settings.app_version}")

#     # Initialize default models with better error handling
#     try:
#         # Initialize OpenAI model only if API key is provided
#         if (
#             settings.openai_api_key
#             and settings.openai_api_key != "your_actual_openai_api_key_here"
#         ):
#             from .models.base import ModelConfig
#             from .models.providers.openai import OpenAIModel

#             openai_config = ModelConfig(
#                 name=settings.default_openai_model,
#                 provider="openai",
#                 description="OpenAI GPT-3.5 Turbo model",
#                 max_tokens=4096,
#                 context_window=16385,
#                 capabilities=["text-generation", "chat", "completion"],
#             )
#             openai_model = OpenAIModel(openai_config, settings.openai_api_key)
#             await model_registry.register_model(openai_model)
#             logger.info(f"OpenAI model '{settings.default_openai_model}' initialized")
#         else:
#             logger.warning(
#                 "OpenAI API key not provided. OpenAI models will not be available."
#             )

#         # Initialize Anthropic model only if API key is provided
#         if (
#             settings.anthropic_api_key
#             and settings.anthropic_api_key != "your_actual_anthropic_api_key_here"
#         ):
#             from .models.providers.anthropic import AnthropicModel

#             anthropic_config = ModelConfig(
#                 name=settings.default_anthropic_model,
#                 provider="anthropic",
#                 description="Anthropic Claude 2 model",
#                 max_tokens=4096,
#                 context_window=100000,
#                 capabilities=["text-generation", "long-context"],
#             )
#             anthropic_model = AnthropicModel(
#                 anthropic_config, settings.anthropic_api_key
#             )
#             await model_registry.register_model(anthropic_model)
#             logger.info(
#                 f"Anthropic model '{settings.default_anthropic_model}' initialized"
#             )
#         else:
#             logger.warning(
#                 "Anthropic API key not provided. "
#                 "Anthropic models will not be available."
#             )

#         # Initialize HuggingFace model (always available as it's local)
#         from .models.providers.huggingface import HuggingFaceModel

#         hf_config = ModelConfig(
#             name=settings.default_huggingface_model,
#             provider="huggingface",
#             description="HuggingFace GPT-2 model",
#             max_tokens=1024,
#             context_window=1024,
#             capabilities=["text-generation"],
#         )
#         hf_model = HuggingFaceModel(hf_config)
#         await model_registry.register_model(hf_model)

#         logger.info(
#             "HuggingFace model '%s' registered",
#             settings.default_huggingface_model,
#         )

#         # Register a test custom model for development
#         from .models.providers.custom import CustomModel

#         async def test_generate(prompt, parameters):
#             return f"Test response to: {prompt}"

#         async def test_stream(prompt, parameters):
#             for word in prompt.split():
#                 yield word + " "
#                 await asyncio.sleep(0.1)

#         test_config = ModelConfig(
#             name="test-model",
#             provider="custom",
#             description="Test model for development",
#         )
#         test_model = CustomModel(test_config, test_generate, test_stream)
#         await model_registry.register_model(test_model)
#         logger.info("Test custom model registered")

#     except Exception as e:
#         logger.error(f"Error initializing models: {e}")
#         # Don't crash the app, just log the error


async def startup():
    """Initialize the application"""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")

    # Initialize default models with better error handling
    try:
        # Always register the test custom model for development
        from .models.base import ModelConfig
        from .models.providers.custom import CustomModel

        async def test_generate(prompt, parameters):
            return f"Test response to: {prompt}"

        async def test_stream(prompt, parameters):
            for word in prompt.split():
                yield word + " "

        test_config = ModelConfig(
            name="test-model", provider="custom", description="Test model for development"
        )

        test_model = CustomModel(test_config, test_generate, test_stream)
        await model_registry.register_model(test_model)
        logger.info("Test custom model registered")

    except Exception as e:
        logger.error(f"Error initializing test model: {e}")
        import traceback

        logger.error(f"Traceback: {traceback.format_exc()}")


async def shutdown():
    """Cleanup application resources"""
    logger.info("Shutting down inferaAPI")


async def homepage(request):
    """Redirect to API documentation"""
    return RedirectResponse(url="/api/docs")


# Create application - THIS MUST BE AT MODULE LEVEL
app = Starlette(
    debug=settings.debug,
    routes=[
        Route("/", homepage),
        Mount("/api", routes=all_routes),
    ],
    middleware=[
        Middleware(GZipMiddleware, minimum_size=1000),
        Middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_methods=["*"],
            allow_headers=["*"],
            allow_credentials=True,
        ),
    ],
    on_startup=[startup],
    on_shutdown=[shutdown],
)


def main():
    """Main entry point for the application"""
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Server will run on http://{settings.host}:{settings.port}")
    print(f"API documentation: http://{settings.host}:{settings.port}/api/docs")
    print("\nNote: Make sure to set up your API keys in the .env file")

    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        workers=settings.workers,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
