#!/usr/bin/env python3
"""
Basic usage example for inferaAPI
"""

import asyncio
import requests
import json

async def main():
    # Example using the REST API
    base_url = "http://localhost:8000/api"
    
    # Test health endpoint
    response = requests.get(f"{base_url}/health")
    print("Health check:", response.json())
    
    # Generate text
    payload = {
        "prompt": "Explain quantum computing in simple terms",
        "provider": "custom",
        "model": "test-model",
        "max_tokens": 50,
        "temperature": 0.7
    }
    
    response = requests.post(f"{base_url}/generate", json=payload)
    if response.status_code == 200:
        result = response.json()
        print("Generated text:", result["text"])
    else:
        print("Error:", response.json())

if __name__ == "__main__":
    asyncio.run(main())