from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class LLMRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prompt: str = Field(..., description="The input prompt for the LLM")
    max_tokens: Optional[int] = Field(
        100, ge=1, le=4096, description="Maximum number of tokens to generate"
    )
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature")
    top_p: Optional[float] = Field(1.0, ge=0.0, le=1.0, description="Nucleus sampling parameter")
    stop_sequences: Optional[List[str]] = Field(None, description="Sequences to stop generation")
    stream: Optional[bool] = Field(False, description="Whether to stream the response")
    model: Optional[str] = Field(None, description="Specific model to use (overrides default)")
    provider: str = Field(..., description="LLM provider (openai, anthropic, huggingface, custom)")


class BatchLLMRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    requests: List[LLMRequest] = Field(..., description="List of LLM requests to process")


class ComparisonRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prompt: str = Field(..., description="The input prompt for all models")
    models: List[Dict[str, Any]] = Field(..., description="List of model configurations to compare")


class ModelRegistrationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., description="Name of the custom model")
    description: Optional[str] = Field(None, description="Description of the model")
    generate_fn: Optional[str] = Field(
        None, description="Path to generation function (for advanced use)"
    )
