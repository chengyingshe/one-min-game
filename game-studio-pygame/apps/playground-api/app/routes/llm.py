from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models import LLMRequest, LLMResponse
from app.config import settings
from app.services import llm_service

router = APIRouter(prefix="/api/llm", tags=["llm"])


@router.post("/chat", response_model=LLMResponse)
def chat(request: LLMRequest):
    if not settings.DEEPSEEK_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="LLM service not configured (missing DEEPSEEK_API_KEY)",
        )

    try:
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        result = llm_service.chat(
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"LLM provider error: {str(e)[:500]}",
        )

    return LLMResponse(**result)
