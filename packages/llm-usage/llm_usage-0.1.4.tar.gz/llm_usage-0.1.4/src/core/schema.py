from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional
import json
import uuid


def generate_request_id() -> str:
    return uuid.uuid4().hex


def utc_now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="milliseconds") + "Z"


@dataclass
class CallParameters:
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    max_tokens: Optional[int] = None
    stop: Optional[List[str]] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    seed: Optional[int] = None

    def to_json(self) -> str:
        return json.dumps({k: v for k, v in asdict(self).items() if v is not None})


@dataclass
class PromptContext:
    system_prompt_id: Optional[str] = None
    system_prompt_version: Optional[str] = None
    template_id: Optional[str] = None
    template_version: Optional[str] = None
    input_preview: Optional[str] = None

    def to_json(self) -> str:
        return json.dumps({k: v for k, v in asdict(self).items() if v is not None})


@dataclass
class RateLimitInfo:
    limit: Optional[int] = None
    remaining: Optional[int] = None
    reset_ms: Optional[int] = None
    retry_after_ms: Optional[int] = None

    def to_json(self) -> str:
        return json.dumps({k: v for k, v in asdict(self).items() if v is not None})


@dataclass
class ErrorInfo:
    error_type: Optional[str] = None
    error_code: Optional[str] = None
    message: Optional[str] = None
    is_rate_limited: bool = False

    def to_json(self) -> str:
        return json.dumps({k: v for k, v in asdict(self).items() if v is not None})


@dataclass
class RequestRecord:
    # identifiers
    request_id: str = field(default_factory=generate_request_id)
    call_id: Optional[str] = None  # logical call grouping across retries/fallbacks
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    # classification
    provider: str = ""  # e.g., "openai", "gemini"
    model: str = ""     # e.g., "gpt-4o-mini"
    api_key_alias: Optional[str] = None  # which key alias was used
    environment: Optional[str] = None
    app_version: Optional[str] = None

    # grouping
    tags: List[str] = field(default_factory=list)

    # inputs
    context: Optional[PromptContext] = None
    parameters: Optional[CallParameters] = None
    input_text: Optional[str] = None  # to enable replay; can be redacted by caller

    # metrics (tokens)
    input_tokens: int = 0
    output_tokens: int = 0
    reasoning_tokens: int = 0
    cached_input_tokens: int = 0

    # latency
    latency_ms: Optional[int] = None
    time_to_first_token_ms: Optional[int] = None
    stream_duration_ms: Optional[int] = None

    # costs
    input_cost_usd: float = 0.0
    cached_input_cost_usd: float = 0.0
    output_cost_usd: float = 0.0
    reasoning_cost_usd: float = 0.0
    total_cost_usd: float = 0.0

    # results
    finish_reason: Optional[str] = None
    response_text_len: Optional[int] = None
    response_text: Optional[str] = None
    success: bool = True

    # operational
    retry_count: int = 0
    rate_limit: Optional[RateLimitInfo] = None
    error: Optional[ErrorInfo] = None

    # streaming diagnostics
    stream_chunk_count: int = 0
    stream_avg_chunk_chars: Optional[float] = None

    def to_row(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "call_id": self.call_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "provider": self.provider,
            "model": self.model,
            "api_key_alias": self.api_key_alias,
            "environment": self.environment,
            "app_version": self.app_version,
            "tags": json.dumps(self.tags) if self.tags else None,
            "context_json": self.context.to_json() if self.context else None,
            "parameters_json": self.parameters.to_json() if self.parameters else None,
            "input_text": self.input_text,
            "input_tokens": self.input_tokens,
            "cached_input_tokens": self.cached_input_tokens,
            "output_tokens": self.output_tokens,
            "reasoning_tokens": self.reasoning_tokens,
            "latency_ms": self.latency_ms,
            "ttft_ms": self.time_to_first_token_ms,
            "stream_duration_ms": self.stream_duration_ms,
            "input_cost_usd": self.input_cost_usd,
            "cached_input_cost_usd": self.cached_input_cost_usd,
            "output_cost_usd": self.output_cost_usd,
            "reasoning_cost_usd": self.reasoning_cost_usd,
            "total_cost_usd": self.total_cost_usd,
            "finish_reason": self.finish_reason,
            "response_text_len": self.response_text_len,
            "response_text": self.response_text,
            "success": 1 if self.success else 0,
            "retry_count": self.retry_count,
            "rate_limit_json": self.rate_limit.to_json() if self.rate_limit else None,
            "error_json": self.error.to_json() if self.error else None,
            "stream_chunk_count": self.stream_chunk_count,
            "stream_avg_chunk_chars": self.stream_avg_chunk_chars,
        }


@dataclass
class StreamChunkRecord:
    request_id: str
    idx: int
    created_at: str = field(default_factory=utc_now_iso)
    delta_text_len: int = 0

    def to_row(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "idx": self.idx,
            "created_at": self.created_at,
            "delta_text_len": self.delta_text_len,
        }


