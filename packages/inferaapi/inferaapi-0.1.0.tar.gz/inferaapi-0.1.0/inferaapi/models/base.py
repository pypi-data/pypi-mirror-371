from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ModelConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    provider: str
    description: Optional[str] = None
    max_tokens: Optional[int] = None
    context_window: Optional[int] = None
    capabilities: List[str] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)


class LLMRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prompt: str = Field(..., description="The input prompt for the LLM")
    max_tokens: Optional[int] = Field(100, description="Maximum number of tokens to generate")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature")
    top_p: Optional[float] = Field(1.0, ge=0.0, le=1.0, description="Nucleus sampling parameter")
    stop_sequences: Optional[List[str]] = Field(None, description="Sequences to stop generation")
    stream: Optional[bool] = Field(False, description="Whether to stream the response")
    model: Optional[str] = Field(None, description="Specific model to use (overrides default)")
    provider: str = Field(..., description="LLM provider (openai, anthropic, huggingface, custom)")


class LLMResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str
    model: str
    provider: str
    tokens_used: Optional[int] = None
    finish_reason: Optional[str] = None
    processing_time: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class StreamResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str
    model: str
    provider: str
    finished: bool = False


class BaseLLMModel(ABC):
    """Abstract base class for all LLM providers"""

    def __init__(self, model_config: ModelConfig):
        self.config = model_config
        self.model_name = model_config.name

    @abstractmethod
    async def initialize(self):
        """Initialize the model (load weights, connect to API, etc.)"""

    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate text from a prompt"""

    @abstractmethod
    async def stream_generate(self, request: LLMRequest) -> AsyncGenerator[StreamResponse, None]:
        """Stream generated text"""

    async def get_info(self) -> Dict[str, Any]:
        """Get information about the model"""
        return self.config.model_dump()
