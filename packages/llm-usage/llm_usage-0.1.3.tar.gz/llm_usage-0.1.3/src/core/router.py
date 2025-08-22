from __future__ import annotations

from typing import Tuple, List, Optional

from core.models import ALL_MODELS, get_provider_for_model
from core.fallback import FallbackOrchestrator, FallbackStep
from core.keys import KeyPool
from core.manager import LLMCallManager


def validate_and_route(model: str) -> Tuple[str, str]:
    if model not in ALL_MODELS:
        raise ValueError(f"Unsupported model '{model}'. Must be one of: {', '.join(ALL_MODELS)}")
    provider = get_provider_for_model(model)
    if provider is None:
        raise ValueError(f"Provider not found for model '{model}'")
    return provider, model


def execute_with_fallback(
    *,
    manager: LLMCallManager,
    steps: List[Tuple[str, str, Optional[List[str]], callable]],
    tags: Optional[List[str]] = None,
    input_text: Optional[str] = None,
) -> Tuple[bool, str, str]:
    """
    Steps: list of (provider, model, key_aliases, executor)
    The executor has signature executor(RequestRecord) -> (success: bool, error_message: Optional[str])
    """
    orchestrator = FallbackOrchestrator(manager)
    plan = [
        FallbackStep(provider=p, model=m, key_aliases=ka, executor=ex)
        for (p, m, ka, ex) in steps
    ]
    return orchestrator.run(plan, tags=tags, input_text=input_text)


