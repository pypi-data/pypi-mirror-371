#!/usr/bin/env python3
"""
Example of registering a custom model with inferaAPI
"""

import asyncio
import requests
from inferaapi.models import model_registry

async def custom_generate(prompt, parameters):
    """Custom generation function"""
    # Your custom model logic here
    return f"Custom model response to: {prompt}"

async def custom_stream(prompt, parameters):
    """Custom streaming function"""
    words = prompt.split()
    for i, word in enumerate(words):
        if i < len(words) - 1:
            yield word + " "
        else:
            yield word
        await asyncio.sleep(0.1)

async def main():
    # Register custom model
    await model_registry.register_custom_model(
        "my-custom-model",
        custom_generate,
        custom_stream,
        "My custom language model"
    )
    
    print("Custom model registered successfully!")
    
    # Test the custom model
    model = await model_registry.get_model("custom", "my-custom-model")
    response = await model.generate(
        prompt="Hello custom model",
        max_tokens=20
    )
    
    print("Custom model response:", response.text)

if __name__ == "__main__":
    asyncio.run(main())