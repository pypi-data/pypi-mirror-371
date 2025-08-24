import asyncio
import time
from functools import wraps
from typing import Any, Dict, Optional


def async_retry(max_attempts: int = 3, delay: float = 1.0):
    """Decorator for retrying async functions"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(delay * (2**attempt))  # Exponential backoff
                    else:
                        raise last_exception
            raise last_exception

        return wrapper

    return decorator


def rate_limit(requests_per_minute: int = 60):
    """Simple rate limiting decorator"""
    last_called = 0.0
    min_interval = 60.0 / requests_per_minute

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            nonlocal last_called
            elapsed = time.time() - last_called
            wait_time = max(0, min_interval - elapsed)

            if wait_time > 0:
                await asyncio.sleep(wait_time)

            last_called = time.time()
            return await func(*args, **kwargs)

        return wrapper

    return decorator


class APIResponse:
    """Standardized API response format"""

    @staticmethod
    def success(data: Any = None, message: str = "Success") -> Dict[str, Any]:
        return {
            "status": "success",
            "message": message,
            "data": data,
            "timestamp": time.time(),
        }

    @staticmethod
    def error(message: str, code: int = 500, details: Optional[Dict] = None) -> Dict[str, Any]:
        return {
            "status": "error",
            "message": message,
            "code": code,
            "details": details or {},
            "timestamp": time.time(),
        }


def validate_json_schema(data: Dict, schema: Dict) -> bool:
    """Simple JSON schema validation"""
    # This is a simplified implementation
    # In production, you might want to use a library like jsonschema
    for key, value_type in schema.items():
        if key not in data:
            return False
        if not isinstance(data[key], value_type):
            return False
    return True


def get_model_key(provider: str, model_name: str) -> str:
    """Generate a unique key for model identification"""
    return f"{provider}:{model_name}"


def parse_model_key(model_key: str) -> tuple:
    """Parse model key into provider and model name"""
    if ":" in model_key:
        provider, model_name = model_key.split(":", 1)
        return provider, model_name
    return model_key, None
