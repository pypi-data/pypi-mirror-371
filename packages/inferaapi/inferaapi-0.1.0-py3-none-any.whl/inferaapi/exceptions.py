class InferaAPIException(Exception):
    """Base exception for all inferaAPI errors"""


class ModelNotFoundError(InferaAPIException):
    """Raised when a requested model is not found"""


class ProviderNotAvailableError(InferaAPIException):
    """Raised when a provider is not available"""


class ModelRegistrationError(InferaAPIException):
    """Raised when model registration fails"""


class AuthenticationError(InferaAPIException):
    """Raised when authentication fails"""


class RateLimitExceededError(InferaAPIException):
    """Raised when rate limit is exceeded"""


class ValidationError(InferaAPIException):
    """Raised when input validation fails"""
