"""
inferaAPI - A unified REST API framework for multiple LLM providers
"""

__version__ = "0.1.0"
__author__ = "Pankaj Kumar"
__email__ = "inferaapi@gmail.com"

# Import the main app instance
from .app import app

# Import other important components for easy access
from .config import settings
from .models import model_registry
from .schemas.requests import BatchLLMRequest, ComparisonRequest, LLMRequest
from .schemas.responses import BatchLLMResponse, ComparisonResponse, LLMResponse

__all__ = [
    "app",
    "settings",
    "model_registry",
    "LLMRequest",
    "BatchLLMRequest",
    "ComparisonRequest",
    "LLMResponse",
    "BatchLLMResponse",
    "ComparisonResponse",
]
