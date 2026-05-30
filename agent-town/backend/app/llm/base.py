from abc import ABC, abstractmethod


class BaseLLM(ABC):
    """统一 LLM 接口 — 屏蔽不同厂商 API 差异"""

    @abstractmethod
    async def chat(self, messages: list[dict], temperature: float = 0.8, max_tokens: int = 500) -> str:
        """发送对话请求，返回文本回复"""
        ...

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """生成文本嵌入向量"""
        ...
