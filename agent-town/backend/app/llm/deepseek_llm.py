from __future__ import annotations

import os

from openai import AsyncOpenAI
from sentence_transformers import SentenceTransformer

from app.config import settings
from app.llm.base import BaseLLM


class DeepSeekLLM(BaseLLM):
    """DeepSeek API 适配器 — OpenAI-compatible 协议"""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.LLM_BASE_URL,
        )
        self._embedding_model: SentenceTransformer | None = None

    async def chat(
        self, messages: list[dict], temperature: float = 0.8, max_tokens: int = 500
    ) -> str:
        response = await self.client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        content = response.choices[0].message.content
        return content if content else ""

    async def embed(self, text: str) -> list[float]:
        if self._embedding_model is None:
            local_path = os.path.join(os.path.dirname(__file__), "..", "..", "model_cache")
            if os.path.isdir(local_path):
                self._embedding_model = SentenceTransformer(local_path)
            else:
                self._embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        embedding = self._embedding_model.encode(text, normalize_embeddings=True)
        return embedding.tolist()
