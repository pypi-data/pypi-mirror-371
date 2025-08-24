import asyncio
import time
from typing import AsyncGenerator

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

from ...models.base import BaseLLMModel, ModelConfig
from ...schemas.requests import LLMRequest
from ...schemas.responses import LLMResponse, StreamResponse


class HuggingFaceModel(BaseLLMModel):
    def __init__(self, model_config: ModelConfig, api_key: str = None):
        super().__init__(model_config)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = None
        self.model = None
        self.pipeline = None

    async def initialize(self):
        # Load model in a separate thread to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._load_model)

    def _load_model(self):
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                low_cpu_mem_usage=True,
            )

            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1,
            )
        except Exception as e:
            raise Exception(f"HuggingFace model loading error: {str(e)}")

    async def generate(self, request: LLMRequest) -> LLMResponse:
        start_time = time.time()

        try:
            # Run inference in a separate thread
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._generate_sync,
                request.prompt,
                request.max_tokens,
                request.temperature,
                request.top_p,
                request.stop_sequences,
            )

            processing_time = time.time() - start_time

            return LLMResponse(
                text=result["text"],
                model=self.model_name,
                provider="huggingface",
                tokens_used=result["tokens_used"],
                processing_time=processing_time,
            )
        except Exception as e:
            raise Exception(f"HuggingFace inference error: {str(e)}")

    def _generate_sync(self, prompt, max_tokens, temperature, top_p, stop_sequences):
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=True if temperature > 0 else False,
                pad_token_id=self.tokenizer.eos_token_id,
                stopping_criteria=stop_sequences if stop_sequences else None,
            )

        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        return {
            "text": generated_text[len(prompt) :],  # Return only the generated part
            "tokens_used": len(outputs[0]),
        }

    async def stream_generate(self, request: LLMRequest) -> AsyncGenerator[StreamResponse, None]:
        # For simplicity, we'll generate the full response and then stream it
        # In a real implementation, you would implement proper token-by-token streaming
        response = await self.generate(request)

        for char in response.text:
            yield StreamResponse(token=char, model=self.model_name, provider="huggingface")
            await asyncio.sleep(0.01)  # Simulate streaming

        yield StreamResponse(token="", model=self.model_name, provider="huggingface", finished=True)
