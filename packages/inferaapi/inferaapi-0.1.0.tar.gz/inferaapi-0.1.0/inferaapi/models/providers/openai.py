import time
from typing import AsyncGenerator

from openai import AsyncOpenAI

from ...models.base import BaseLLMModel, ModelConfig
from ...schemas.requests import LLMRequest
from ...schemas.responses import LLMResponse, StreamResponse


class OpenAIModel(BaseLLMModel):
    def __init__(self, model_config: ModelConfig, api_key: str):
        super().__init__(model_config)
        self.client = AsyncOpenAI(api_key=api_key)

    async def initialize(self):
        # Verify API key and model availability
        try:
            models = await self.client.models.list()
            available_models = [model.id for model in models.data]
            if self.model_name not in available_models:
                raise ValueError(f"Model {self.model_name} not available in OpenAI API")
        except Exception as e:
            raise Exception(f"OpenAI API initialization error: {str(e)}")

    async def generate(self, request: LLMRequest) -> LLMResponse:
        start_time = time.time()
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": request.prompt}],
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                top_p=request.top_p,
                stop=request.stop_sequences if request.stop_sequences else None,
            )

            processing_time = time.time() - start_time

            return LLMResponse(
                text=response.choices[0].message.content,
                model=response.model,
                provider="openai",
                tokens_used=response.usage.total_tokens if response.usage else None,
                finish_reason=response.choices[0].finish_reason,
                processing_time=processing_time,
            )
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    async def stream_generate(self, request: LLMRequest) -> AsyncGenerator[StreamResponse, None]:
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": request.prompt}],
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                top_p=request.top_p,
                stop=request.stop_sequences if request.stop_sequences else None,
                stream=True,
            )

            async for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    yield StreamResponse(token=content, model=self.model_name, provider="openai")

            yield StreamResponse(token="", model=self.model_name, provider="openai", finished=True)
        except Exception as e:
            yield StreamResponse(
                token=f"Error: {str(e)}",
                model=self.model_name,
                provider="openai",
                finished=True,
            )
