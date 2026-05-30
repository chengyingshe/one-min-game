"""DeepSeek LLM service — OpenAI-compatible API wrapper."""

from __future__ import annotations

import json
import logging
import os

import requests

from app.config import settings

log = logging.getLogger("llm_service")

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")


def chat(
    messages: list[dict],
    temperature: float = 0.7,
    max_tokens: int = 300,
) -> dict:
    """Call DeepSeek chat API with OpenAI-compatible format."""
    if not DEEPSEEK_API_KEY:
        log.warning("DEEPSEEK_API_KEY not set, returning fallback")
        return _fallback(messages)

    url = f"{DEEPSEEK_BASE_URL}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return {
            "content": data["choices"][0]["message"]["content"],
            "model": data.get("model", DEEPSEEK_MODEL),
        }
    except Exception as exc:
        log.error("DeepSeek API error: %s", exc)
        if hasattr(exc, "response") and exc.response is not None:
            log.error("Response body: %s", exc.response.text[:500])
        return _fallback(messages)


def _fallback(messages: list[dict]) -> dict:
    """Return a generic fallback when LLM is unavailable."""
    return {"content": "诸位且慢，容老衲思量片刻。（LLM未配置，使用默认文本）"}
