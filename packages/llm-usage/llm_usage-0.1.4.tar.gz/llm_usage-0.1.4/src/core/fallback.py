from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, List, Optional, Sequence, Tuple, Dict, Any
import time
import uuid

from .manager import LLMCallManager
from .schema import RateLimitInfo, RequestRecord
from .keys import KeyPool


# Executor: takes (call_id, api_key_alias) and returns (success, request_id, error_message, response_dict)
Retryable = Callable[[str, Optional[str]], Tuple[bool, Optional[str], Optional[str], Optional[Dict[str, Any]]]]


@dataclass
class FallbackStep:
    provider: str
    model: str
    # The executor is injected by provider-specific adapters later.
    # It should execute the call and return (success, error_message).
    executor: Retryable
    # Optional cooldown before attempting this step (ms)
    cooldown_ms: int = 0
    # Optional ordered list of api key aliases to try for this step
    key_aliases: Optional[List[str]] = None


class FallbackOrchestrator:
    def __init__(self, manager: LLMCallManager):
        self.manager = manager

    def run(self, steps: Sequence[FallbackStep], *, tags: Optional[List[str]] = None, input_text: Optional[str] = None, key_pool: Optional[KeyPool] = None) -> Tuple[bool, str, str, Optional[Dict[str, Any]]]:
        """
        Execute a sequence of fallback steps until one succeeds.
        Returns (success, request_id, call_id). If all fail, success is False and request_id is the last attempt.
        """
        call_id = uuid.uuid4().hex
        last_request_id = ""
        last_response: Optional[Dict[str, Any]] = None
        for idx, step in enumerate(steps):
            if step.cooldown_ms > 0:
                time.sleep(step.cooldown_ms / 1000.0)
            # Try provided key aliases (or a single None entry to try without alias)
            keys_to_try: List[Optional[str]] = step.key_aliases or [None]
            for key_attempt_index, key_alias in enumerate(keys_to_try):
                try:
                    ok, req_id, err, resp = step.executor(call_id, key_alias)
                    if req_id:
                        last_request_id = req_id
                    if ok:
                        return True, last_request_id, call_id, resp
                    else:
                        continue
                except Exception:
                    continue
        return False, last_request_id, call_id, last_response


