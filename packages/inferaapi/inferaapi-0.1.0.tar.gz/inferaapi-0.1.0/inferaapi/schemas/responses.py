# inferaapi/schemas/responses.py
from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


# ---------- Non-stream responses (your existing models) ----------
class LLMResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(..., description="The generated text")
    model: str = Field(..., description="The model used for generation")
    provider: str = Field(..., description="The provider of the model")
    tokens_used: Optional[int] = Field(None, description="Number of tokens used")
    finish_reason: Optional[str] = Field(None, description="Reason for generation stopping")
    processing_time: Optional[float] = Field(
        None, description="Time taken for generation in seconds"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class BatchLLMResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    responses: List[LLMResponse] = Field(..., description="List of responses")


class ComparisonResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prompt: str = Field(..., description="The input prompt used for comparison")
    results: Dict[str, LLMResponse] = Field(..., description="Results for each model")


class ModelInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(..., description="Name of the model")
    provider: str = Field(..., description="Provider of the model")
    description: Optional[str] = Field(None, description="Description of the model")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens supported")
    context_window: Optional[int] = Field(None, description="Context window size")
    capabilities: List[str] = Field(default_factory=list, description="Capabilities of the model")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Model parameters")


class ModelsListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    models: Dict[str, ModelInfo] = Field(..., description="List of available models")


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: str = Field(..., description="Overall status of the API")
    providers: Dict[str, bool] = Field(..., description="Status of each provider")
    models: Dict[str, bool] = Field(..., description="Status of each model")
    version: str = Field(..., description="API version")


class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    error: str = Field(..., description="Error message")
    code: int = Field(..., description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


# ---------- Streaming responses (new) ----------
class StreamDelta(BaseModel):
    model_config = ConfigDict(extra="forbid")
    # text delta for text/chat
    content: Optional[str] = Field(None, description="Delta content token(s)")
    role: Optional[str] = Field(None, description="Role for chat deltas, typically 'assistant'")


class StreamChoice(BaseModel):
    model_config = ConfigDict(extra="forbid")
    index: int = Field(..., description="Choice index")
    delta: StreamDelta = Field(..., description="Incremental delta")
    finish_reason: Optional[str] = Field(None, description="Reason if this choice finished")


class StreamChunk(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: Optional[str] = Field(None, description="Chunk id from provider")
    model: str = Field(..., description="Model producing the chunk")
    created: int = Field(..., description="Unix seconds")
    object: Literal["chat.completion.chunk", "text_completion.chunk"] = Field(
        "chat.completion.chunk", description="Type tag of the chunk"
    )
    choices: List[StreamChoice] = Field(..., description="Chunk choices")


class StreamEnd(BaseModel):
    model_config = ConfigDict(extra="forbid")
    object: Literal["completion.end"] = Field("completion.end", description="End sentinel")
    model: str = Field(..., description="Model that produced the completion")
    created: int = Field(..., description="Unix seconds")
    usage: Optional[Dict[str, Any]] = Field(None, description="Optional token usage summary")


# Public alias used by providers
StreamResponse = Union[StreamChunk, StreamEnd]
