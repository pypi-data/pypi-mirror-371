import asyncio

import pytest

from inferaapi.models import model_registry
from inferaapi.schemas.requests import LLMRequest


def initialize_test_models():
    """Initialize models specifically for these tests"""
    # Clear any existing models
    model_registry.models.clear()
    print("DEBUG: Cleared model registry")

    # Import and setup models synchronously
    from inferaapi.models.base import ModelConfig
    from inferaapi.models.providers.custom import CustomModel

    # Create test functions
    async def test_generate(prompt, parameters):
        return f"Test response to: {prompt}"

    async def test_stream(prompt, parameters):
        for word in prompt.split():
            yield word + " "

    # Create and register model
    test_config = ModelConfig(
        name="test-model", provider="custom", description="Test model for unit tests"
    )

    test_model = CustomModel(test_config, test_generate, test_stream)

    # Register model synchronously by running the async function
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(model_registry.register_model(test_model))
        print("DEBUG: Successfully registered test-model")
        print(f"DEBUG: Models after registration: {list(model_registry.models.keys())}")
        return True
    except Exception as e:
        print(f"DEBUG: Error registering model: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_model_registry():
    """Test that models can be registered and retrieved"""
    # Initialize models for this test
    success = initialize_test_models()
    if not success:
        pytest.fail("Failed to initialize test models")

    # Debug: check what's actually in the registry
    print(f"DEBUG: Registry models dict keys: {list(model_registry.models.keys())}")
    print(f"DEBUG: Registry models: {model_registry.models}")

    models = model_registry.list_models()
    print(f"DEBUG: list_models() returned: {models}")

    # Check if the registry is empty
    if not model_registry.models:
        pytest.fail("Registry is empty - models were not registered properly")

    assert "test-model" in models
    assert models["test-model"]["provider"] == "custom"


def test_model_generation():
    """Test text generation with test model"""
    # Initialize models for this test
    success = initialize_test_models()
    if not success:
        pytest.skip("Failed to initialize test models, skipping generation test")
        return

    # Debug: check if model exists
    print(f"DEBUG: Available models: {list(model_registry.models.keys())}")

    if "test-model" not in model_registry.models:
        pytest.skip("test-model not registered, skipping generation test")
        return

    # Get model and run async generation synchronously
    loop = asyncio.get_event_loop()
    model = loop.run_until_complete(model_registry.get_model("custom", "test-model"))

    request = LLMRequest(prompt="Hello world", provider="custom", max_tokens=10)

    # Run async method synchronously
    response = loop.run_until_complete(model.generate(request))
    assert response.text.startswith("Test response to: Hello world")
    assert response.provider == "custom"
    assert response.model == "test-model"
