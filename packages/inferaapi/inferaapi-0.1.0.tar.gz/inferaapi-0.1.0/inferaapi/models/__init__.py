from typing import Any, Dict, Optional

from ..config import settings
from .base import BaseLLMModel, ModelConfig
from .providers import AnthropicModel, CustomModel, HuggingFaceModel, OpenAIModel


class ModelRegistry:
    """Registry for managing all available models"""

    def __init__(self):
        self.models: Dict[str, BaseLLMModel] = {}
        self.default_models: Dict[str, str] = {
            "openai": settings.default_openai_model,
            "anthropic": settings.default_anthropic_model,
            "huggingface": settings.default_huggingface_model,
            "custom": "test-model",  # Add custom provider
        }

    async def register_model(self, model: BaseLLMModel):
        """Register a model instance"""
        await model.initialize()
        # Use just the model name as key, not provider:model_name
        self.models[model.model_name] = model

    async def get_model(self, provider: str, model_name: Optional[str] = None) -> BaseLLMModel:
        """Get a model instance by provider and optional model name"""
        if not model_name:
            model_name = self.default_models.get(provider)

        if not model_name:
            raise ValueError(f"No default model defined for provider: {provider}")

        # Look for the model by its name only
        if model_name not in self.models:
            await self._create_model(provider, model_name)

        return self.models[model_name]

    async def _create_model(self, provider: str, model_name: str):
        """Create a new model instance"""
        config = ModelConfig(
            name=model_name, provider=provider, description=f"{provider} model: {model_name}"
        )

        if provider == "openai":
            model = OpenAIModel(config, settings.openai_api_key)
        elif provider == "anthropic":
            model = AnthropicModel(config, settings.anthropic_api_key)
        elif provider == "huggingface":
            model = HuggingFaceModel(config, settings.huggingface_api_key)
        elif provider == "custom":
            # For custom models, we need to provide the functions
            async def generate_fn(prompt, parameters):
                return f"Test response to: {prompt}"

            async def stream_fn(prompt, parameters):
                for word in prompt.split():
                    yield word + " "

            model = CustomModel(config, generate_fn, stream_fn)
        else:
            raise ValueError(f"Unknown provider: {provider}")

        await self.register_model(model)

    async def register_custom_model(
        self,
        model_name: str,
        generate_fn: callable,
        stream_fn: callable = None,
        description: str = "Custom model",
    ):
        """Register a custom model with custom inference functions"""
        config = ModelConfig(name=model_name, provider="custom", description=description)

        model = CustomModel(config, generate_fn, stream_fn)
        await self.register_model(model)

    def list_models(self) -> Dict[str, Any]:
        """List all registered models - synchronous version"""
        return {
            name: {
                "name": model.model_name,
                "provider": model.config.provider,
                "description": model.config.description,
            }
            for name, model in self.models.items()
        }


# Global model registry
model_registry = ModelRegistry()
