from __future__ import annotations

import time
from typing import Iterable, List, Optional

from .schema import RequestRecord, StreamChunkRecord, RateLimitInfo, ErrorInfo
from .storage import SQLiteStore
from .pricing import compute_costs_for_model


class LLMCallManager:
    def __init__(self, db_path: str):
        self.store = SQLiteStore(db_path)

    def start_request(self, provider: str, model: str, *, tags: Optional[List[str]] = None, input_text: Optional[str] = None, call_id: Optional[str] = None, api_key_alias: Optional[str] = None) -> RequestRecord:
        record = RequestRecord(provider=provider, model=model, tags=tags or [], input_text=input_text, call_id=call_id, api_key_alias=api_key_alias)
        self.store.upsert_request(record.to_row())
        return record

    def record_parameters(self, record: RequestRecord, *, parameters_json: Optional[str] = None) -> None:
        if parameters_json is not None:
            record.parameters = None  # raw json string path not used; keep schema object path for future
        record.updated_at = record.updated_at  # no-op to satisfy lints; updated in upsert
        self.store.upsert_request(record.to_row())

    def finalize_success(self, record: RequestRecord, *, input_tokens: int, output_tokens: int, reasoning_tokens: int = 0, cached_input_tokens: int = 0,
                         latency_ms: Optional[int] = None, ttft_ms: Optional[int] = None, stream_duration_ms: Optional[int] = None,
                         finish_reason: Optional[str] = None, response_text_len: Optional[int] = None, response_text: Optional[str] = None,
                         stream_chunk_count: int = 0, stream_avg_chunk_chars: Optional[float] = None) -> None:
        record.input_tokens = input_tokens
        record.cached_input_tokens = cached_input_tokens
        record.output_tokens = output_tokens
        record.reasoning_tokens = reasoning_tokens
        record.latency_ms = latency_ms
        record.time_to_first_token_ms = ttft_ms
        record.stream_duration_ms = stream_duration_ms
        record.finish_reason = finish_reason
        record.response_text_len = response_text_len
        record.response_text = response_text
        record.stream_chunk_count = stream_chunk_count
        record.stream_avg_chunk_chars = stream_avg_chunk_chars
        costs = compute_costs_for_model(record.model, input_tokens, output_tokens, reasoning_tokens, cached_input_tokens)
        record.input_cost_usd = costs["input_cost_usd"]
        record.cached_input_cost_usd = costs["cached_input_cost_usd"]
        record.output_cost_usd = costs["output_cost_usd"]
        record.reasoning_cost_usd = costs["reasoning_cost_usd"]
        record.total_cost_usd = costs["total_cost_usd"]
        record.success = True
        self.store.upsert_request(record.to_row())

    def finalize_error(self, record: RequestRecord, *, error_type: str, message: str, error_code: Optional[str] = None,
                        retry_count: int = 0, is_rate_limited: bool = False, rate_limit: Optional[RateLimitInfo] = None) -> None:
        record.success = False
        record.retry_count = retry_count
        record.error = ErrorInfo(error_type=error_type, error_code=error_code, message=message, is_rate_limited=is_rate_limited)
        record.rate_limit = rate_limit
        self.store.upsert_request(record.to_row())

    def record_stream_chunks(self, record: RequestRecord, deltas: Iterable[int]) -> None:
        rows = []
        for idx, delta_len in enumerate(deltas):
            rows.append(StreamChunkRecord(request_id=record.request_id, idx=idx, delta_text_len=delta_len).to_row())
        self.store.insert_stream_chunks(rows)

    def get_request(self, request_id: str):
        return self.store.get_request(request_id)

    def list_requests(self, **kwargs):
        return self.store.list_requests(**kwargs)

    def summarize_call_cost(self, call_id: str) -> float:
        # Sum total cost across attempts for a logical call
        requests = self.store.list_requests(limit=1000, offset=0, filters={})
        total = 0.0
        for r in requests:
            if r.get("call_id") == call_id:
                total += float(r.get("total_cost_usd") or 0.0)
        return round(total, 6)


