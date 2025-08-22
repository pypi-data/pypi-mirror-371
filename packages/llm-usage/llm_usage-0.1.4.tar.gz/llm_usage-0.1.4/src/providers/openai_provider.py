from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Tuple, Union

from openai import OpenAI

from core.manager import LLMCallManager
from core.schema import CallParameters
from core.keys import KeyPool


InputType = Union[str, List[Dict[str, Any]]]


class OpenAIProvider:
    def __init__(self, manager: LLMCallManager, key_pool: KeyPool):
        self.manager = manager
        self.key_pool = key_pool

    def _get_client(self, api_key_alias: Optional[str]) -> Tuple[OpenAI, Optional[str]]:
        alias = api_key_alias if api_key_alias is not None else (self.key_pool.all_aliases()[0] if self.key_pool.all_aliases() else None)
        api_key_value = None
        if alias is not None:
            key = self.key_pool.get_by_alias(alias)
            if key is None:
                raise ValueError(f"Unknown OpenAI key alias '{alias}'. Available: {self.key_pool.all_aliases()}")
            api_key_value = key.value
        client = OpenAI(api_key=api_key_value) if api_key_value else OpenAI()
        return client, alias

    def _map_parameters(self, params: Optional[CallParameters]) -> Dict[str, Any]:
        if params is None:
            return {}
        payload: Dict[str, Any] = {}
        if params.temperature is not None:
            payload["temperature"] = params.temperature
        if params.top_p is not None:
            payload["top_p"] = params.top_p
        if params.max_tokens is not None:
            # Responses API uses max_output_tokens
            payload["max_output_tokens"] = params.max_tokens
        # penalties/seed not universally supported on Responses yet; omit unless needed
        return payload

    @staticmethod
    def _get_field(obj: Any, key: str, default: Any = None) -> Any:
        if obj is None:
            return default
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    @staticmethod
    def _extract_output_text(resp: Any) -> Optional[str]:
        text = getattr(resp, "output_text", None)
        if isinstance(text, str):
            return text
        # Fallback: try to construct from output array
        output = getattr(resp, "output", None)
        if isinstance(output, list):
            parts: List[str] = []
            for item in output:
                if isinstance(item, dict):
                    if item.get("type") == "message":
                        for c in item.get("content", []) or []:
                            if isinstance(c, dict) and c.get("type") == "output_text":
                                t = c.get("text")
                                if isinstance(t, str):
                                    parts.append(t)
                else:
                    # best-effort string cast
                    try:
                        s = str(item)
                        if s:
                            parts.append(s)
                    except Exception:
                        pass
            if parts:
                return "".join(parts)
        return None

    def call(self, *, model: str, input: InputType, instructions: Optional[str] = None,
             parameters: Optional[CallParameters] = None, api_key_alias: Optional[str] = None,
             tags: Optional[List[str]] = None, call_id: Optional[str] = None,
             structured_schema: Optional[type] = None) -> Dict[str, Any]:
        client, used_alias = self._get_client(api_key_alias)
        record = self.manager.start_request("openai", model, tags=tags, input_text=(input if isinstance(input, str) else None), call_id=call_id, api_key_alias=used_alias)
        started = time.perf_counter()
        try:
            payload: Dict[str, Any] = {"model": model, "input": input}
            if instructions is not None:
                payload["instructions"] = instructions
            payload.update(self._map_parameters(parameters))

            if structured_schema is not None:
                resp = client.responses.parse(**payload, text_format=structured_schema)
            else:
                resp = client.responses.create(**payload)

            latency_ms = int((time.perf_counter() - started) * 1000)

            # Extract usage and text
            usage = getattr(resp, "usage", None) or {}
            input_tokens = int(self._get_field(usage, "input_tokens", 0) or 0)
            input_tokens_details = self._get_field(usage, "input_tokens_details", {}) or {}
            cached_tokens = int(self._get_field(input_tokens_details, "cached_tokens", 0) or 0)
            output_tokens = int(self._get_field(usage, "output_tokens", 0) or 0)
            output_tokens_details = self._get_field(usage, "output_tokens_details", {}) or {}
            reasoning_tokens = int(self._get_field(output_tokens_details, "reasoning_tokens", 0) or 0)

            output_text = self._extract_output_text(resp)
            response_text_len = len(output_text) if isinstance(output_text, str) else None
            status = self._get_field(resp, "status", None)

            self.manager.finalize_success(
                record,
                input_tokens=input_tokens,
                cached_input_tokens=cached_tokens,
                output_tokens=output_tokens,
                reasoning_tokens=reasoning_tokens,
                latency_ms=latency_ms,
                finish_reason=status,
                response_text_len=response_text_len,
                response_text=output_text,
            )

            return {
                "request_id": record.request_id,
                "call_id": record.call_id,
                "output_text": output_text,
                "output_parsed": getattr(resp, "output_parsed", None),
                "raw_response": resp,
            }
        except Exception as exc:
            self.manager.finalize_error(record, error_type=exc.__class__.__name__, message=str(exc))
            raise

    def call_stream(self, *, model: str, input: InputType, instructions: Optional[str] = None,
                    parameters: Optional[CallParameters] = None, api_key_alias: Optional[str] = None,
                    tags: Optional[List[str]] = None, call_id: Optional[str] = None) -> Dict[str, Any]:
        client, used_alias = self._get_client(api_key_alias)
        record = self.manager.start_request("openai", model, tags=tags, input_text=(input if isinstance(input, str) else None), call_id=call_id, api_key_alias=used_alias)
        started = time.perf_counter()
        ttft_ms: Optional[int] = None
        chunk_count = 0
        total_chunk_chars = 0
        final_resp = None
        try:
            payload: Dict[str, Any] = {"model": model, "input": input, "stream": True}
            if instructions is not None:
                payload["instructions"] = instructions
            payload.update(self._map_parameters(parameters))

            stream = client.responses.create(**payload)

            for event in stream:
                if ttft_ms is None:
                    ttft_ms = int((time.perf_counter() - started) * 1000)
                chunk_count += 1
                chunk_str = str(event)
                total_chunk_chars += len(chunk_str)
                text_piece = getattr(event, "output_text", None)
                if isinstance(text_piece, str) and text_piece:
                    print(text_piece, end="", flush=True)
                # capture final response when present
                maybe_resp = getattr(event, "response", None)
                if maybe_resp is not None:
                    final_resp = maybe_resp

            duration_ms = int((time.perf_counter() - started) * 1000)
            avg_chunk_chars = (total_chunk_chars / chunk_count) if chunk_count > 0 else None

            # Prefer final_resp if captured; otherwise stream object may have last event data
            resp = final_resp
            if resp is None:
                # we cannot compute usage without final response; mark zero but still record stream diagnostics
                self.manager.finalize_success(
                    record,
                    input_tokens=0,
                    cached_input_tokens=0,
                    output_tokens=0,
                    reasoning_tokens=0,
                    latency_ms=duration_ms,
                    ttft_ms=ttft_ms,
                    stream_duration_ms=duration_ms,
                    stream_chunk_count=chunk_count,
                    stream_avg_chunk_chars=avg_chunk_chars,
                )
                return {"request_id": record.request_id, "call_id": record.call_id, "output_text": None, "raw_response": None}

            usage = getattr(resp, "usage", None) or {}
            input_tokens = int(self._get_field(usage, "input_tokens", 0) or 0)
            input_tokens_details = self._get_field(usage, "input_tokens_details", {}) or {}
            cached_tokens = int(self._get_field(input_tokens_details, "cached_tokens", 0) or 0)
            output_tokens = int(self._get_field(usage, "output_tokens", 0) or 0)
            output_tokens_details = self._get_field(usage, "output_tokens_details", {}) or {}
            reasoning_tokens = int(self._get_field(output_tokens_details, "reasoning_tokens", 0) or 0)

            output_text = self._extract_output_text(resp)
            response_text_len = len(output_text) if isinstance(output_text, str) else None
            status = self._get_field(resp, "status", None)

            self.manager.finalize_success(
                record,
                input_tokens=input_tokens,
                cached_input_tokens=cached_tokens,
                output_tokens=output_tokens,
                reasoning_tokens=reasoning_tokens,
                latency_ms=duration_ms,
                ttft_ms=ttft_ms,
                stream_duration_ms=duration_ms,
                finish_reason=status,
                response_text_len=response_text_len,
                response_text=output_text,
                stream_chunk_count=chunk_count,
                stream_avg_chunk_chars=avg_chunk_chars,
            )

            return {
                "request_id": record.request_id,
                "call_id": record.call_id,
                "output_text": output_text,
                "raw_response": resp,
            }
        except Exception as exc:
            self.manager.finalize_error(record, error_type=exc.__class__.__name__, message=str(exc))
            raise


