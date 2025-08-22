from __future__ import annotations

from typing import Dict, List, Optional


# Centralized model registries (copied from utils to ensure import-safe module name)
OPENAI_MODELS: List[str] = [
    "gpt-5",
    "gpt-5-mini",
    "gpt-5-nano",
    "gpt-5-chat-latest",
    "o3",
    "o3-mini",
    "o3-deep-research",
    "o4-mini",
    "o4-mini-deep-research",
    "gpt-4.1",
    "gpt-4.1-mini",
    "gpt-4o",
    "gpt-4o-mini",
]


GEMINI_MODELS: List[str] = [
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]


def get_provider_for_model(model: str) -> Optional[str]:
    if model in OPENAI_MODELS:
        return "openai"
    if model in GEMINI_MODELS:
        return "gemini"
    return None


ALL_MODELS: List[str] = OPENAI_MODELS + GEMINI_MODELS


