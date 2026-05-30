"""Test the LLM endpoint and return integration instructions for game projects."""

from __future__ import annotations

import httpx

from pygame_studio_mcp.lib.playground_client import (
    PLAYGROUND_API_URL,
    PlaygroundError,
    api_post,
)

_INTEGRATION_GUIDE = """\
## LLM Integration for Games

The pygame_sdk provides two functions for calling AI from game code:

### Single-shot prompt
```python
from pygame_sdk import ask_llm

response = ask_llm("Generate a riddle", system_prompt="You are a riddle master")
```

### Multi-turn conversation
```python
from pygame_sdk import ask_llm_messages

messages = [
    {"role": "system", "content": "You are a dungeon narrator"},
    {"role": "user", "content": "Describe the next room"},
]
response = ask_llm_messages(messages, max_tokens=128)
```

### Usage tips
- Call LLM during non-time-critical moments (level transitions, dialogue, game-over)
- Keep max_tokens low (64-256) for faster responses
- Both functions return empty string on failure (no crash)
- Import: `from pygame_sdk import ask_llm, ask_llm_messages`
"""


async def add_llm_to_game(
    project: str,
    test_prompt: str | None = None,
    system_prompt: str | None = None,
) -> dict:
    """Test the LLM API endpoint and return integration guide for the game."""
    messages: list[dict] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": test_prompt or "Say hello in one sentence."})

    try:
        result = await api_post("/api/llm/chat", json={
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 64,
        })
        return {
            "success": True,
            "project": project,
            "test_response": result.get("content", ""),
            "model": result.get("model", ""),
            "usage": result.get("usage", {}),
            "sdk_functions": ["ask_llm", "ask_llm_messages"],
            "integration_guide": _INTEGRATION_GUIDE,
        }
    except PlaygroundError as e:
        if e.status_code == 503:
            return {
                "success": False,
                "project": project,
                "error": "LLM service not configured. Set DEEPSEEK_API_KEY environment variable.",
                "sdk_functions": ["ask_llm", "ask_llm_messages"],
                "integration_guide": _INTEGRATION_GUIDE,
            }
        return {
            "success": False,
            "project": project,
            "error": f"LLM API error {e.status_code}: {e.detail}",
        }
    except httpx.ConnectError:
        return {
            "success": False,
            "project": project,
            "error": f"Cannot connect to Playground API at {PLAYGROUND_API_URL}. "
            "Start it with: make playground-up",
            "sdk_functions": ["ask_llm", "ask_llm_messages"],
            "integration_guide": _INTEGRATION_GUIDE,
        }
    except httpx.TimeoutException:
        return {
            "success": False,
            "project": project,
            "error": "LLM API request timed out",
        }
