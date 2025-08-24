import time
from typing import AsyncGenerator

import anthropic

from ...models.base import BaseLLMModel, ModelConfig
from ...schemas.requests import LLMRequest
from ...schemas.responses import LLMResponse, StreamResponse


class AnthropicModel(BaseLLMModel):
    def __init__(self, model_config: ModelConfig, api_key: str):
        super().__init__(model_config)
        self.client = anthropic.AsyncAnthropic(api_key=api_key)

    async def initialize(self):
        # Verify API key
        try:
            await self.client.messages.create(
                model=self.model_name,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hello"}],
            )
        except Exception as e:
            raise Exception(f"Anthropic API initialization error: {str(e)}")

    async def generate(self, request: LLMRequest) -> LLMResponse:
        start_time = time.time()
        try:
            response = await self.client.messages.create(
                model=self.model_name,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                top_p=request.top_p,
                stop_sequences=(request.stop_sequences if request.stop_sequences else None),
                messages=[{"role": "user", "content": request.prompt}],
            )

            processing_time = time.time() - start_time

            return LLMResponse(
                text=response.content[0].text,
                model=self.model_name,
                provider="anthropic",
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                finish_reason=response.stop_reason,
                processing_time=processing_time,
            )
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")

    async def stream_generate(self, request: LLMRequest) -> AsyncGenerator[StreamResponse, None]:
        try:
            with self.client.messages.stream(
                model=self.model_name,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                top_p=request.top_p,
                stop_sequences=(request.stop_sequences if request.stop_sequences else None),
                messages=[{"role": "user", "content": request.prompt}],
            ) as stream:
                async for text in stream.text_stream:
                    yield StreamResponse(token=text, model=self.model_name, provider="anthropic")

            yield StreamResponse(
                token="", model=self.model_name, provider="anthropic", finished=True
            )
        except Exception as e:
            yield StreamResponse(
                token=f"Error: {str(e)}",
                model=self.model_name,
                provider="anthropic",
                finished=True,
            )
