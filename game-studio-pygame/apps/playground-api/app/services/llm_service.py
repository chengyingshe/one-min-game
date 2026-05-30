from __future__ import annotations

from openai import OpenAI

from app.config import settings


def get_client() -> OpenAI:
    return OpenAI(
        api_key=settings.DEEPSEEK_API_KEY,
        base_url=settings.DEEPSEEK_BASE_URL,
    )


def chat(
    messages: list[dict],
    temperature: float = 0.7,
    max_tokens: int = 2048,
) -> dict:
    client = get_client()
    response = client.chat.completions.create(
        model=settings.DEEPSEEK_MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=False,
    )
    choice = response.choices[0]
    return {
        "content": choice.message.content,
        "model": response.model,
        "usage": {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
        }
        if response.usage
        else {},
    }
