import asyncio
import time
from typing import AsyncGenerator, Callable

from ...models.base import BaseLLMModel, ModelConfig
from ...schemas.requests import LLMRequest
from ...schemas.responses import LLMResponse, StreamResponse


class CustomModel(BaseLLMModel):
    """Custom model that allows users to plug in their own inference functions"""

    def __init__(
        self,
        model_config: ModelConfig,
        generate_fn: Callable[[str, dict], str],
        stream_fn: Callable[[str, dict], AsyncGenerator[str, None]] = None,
    ):
        super().__init__(model_config)
        self.generate_fn = generate_fn
        self.stream_fn = stream_fn

    async def initialize(self):
        # No initialization needed for custom functions
        pass

    async def generate(self, request: LLMRequest) -> LLMResponse:
        start_time = time.time()

        try:
            # Run the custom generation function
            if asyncio.iscoroutinefunction(self.generate_fn):
                text = await self.generate_fn(request.prompt, request.dict())
            else:
                loop = asyncio.get_event_loop()
                text = await loop.run_in_executor(
                    None, self.generate_fn, request.prompt, request.dict()
                )

            processing_time = time.time() - start_time

            return LLMResponse(
                text=text,
                model=self.model_name,
                provider="custom",
                processing_time=processing_time,
            )
        except Exception as e:
            raise Exception(f"Custom model error: {str(e)}")

    async def stream_generate(self, request: LLMRequest) -> AsyncGenerator[StreamResponse, None]:
        if not self.stream_fn:
            # Fall back to non-streaming if no stream function provided
            response = await self.generate(request)
            for char in response.text:
                yield StreamResponse(token=char, model=self.model_name, provider="custom")
                await asyncio.sleep(0.01)
        else:
            try:
                # Use the custom streaming function
                async for token in self.stream_fn(request.prompt, request.dict()):
                    yield StreamResponse(token=token, model=self.model_name, provider="custom")
            except Exception as e:
                yield StreamResponse(
                    token=f"Error: {str(e)}", model=self.model_name, provider="custom"
                )

        yield StreamResponse(token="", model=self.model_name, provider="custom", finished=True)
