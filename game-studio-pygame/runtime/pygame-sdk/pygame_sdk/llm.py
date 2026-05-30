"""LLM helper for games to call AI features via the Playground API."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

LLM_API_URL = os.environ.get(
    "LLM_API_URL", "http://localhost:8000/api/llm/chat"
)


def ask_llm(
    prompt: str,
    system_prompt: str = "",
    temperature: float = 0.7,
    max_tokens: int = 256,
) -> str:
    """Send a single prompt to the LLM and return the response text.

    Returns empty string on failure.
    """
    messages: list[dict] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    return ask_llm_messages(messages, temperature=temperature, max_tokens=max_tokens)


def ask_llm_messages(
    messages: list[dict],
    temperature: float = 0.7,
    max_tokens: int = 256,
) -> str:
    """Send multi-turn messages to the LLM and return the response text.

    Each message dict should have "role" and "content" keys.
    Returns empty string on failure.
    """
    body = json.dumps({
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }).encode("utf-8")

    req = urllib.request.Request(
        LLM_API_URL,
        data=body,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        return data.get("content", "")
    except (urllib.error.URLError, OSError, json.JSONDecodeError, KeyError):
        return ""
