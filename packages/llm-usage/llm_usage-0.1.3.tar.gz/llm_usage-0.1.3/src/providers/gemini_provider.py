from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Tuple, Union

from google import genai
from google.genai import types

from core.manager import LLMCallManager
from core.schema import CallParameters
from core.keys import KeyPool


InputType = Union[str, List[str], List[Dict[str, Any]]]


class GeminiProvider:
    def __init__(self, manager: LLMCallManager, key_pool: KeyPool):
        self.manager = manager
        self.key_pool = key_pool

    def _get_client(self, api_key_alias: Optional[str]) -> Tuple[genai.Client, Optional[str]]:
        alias = api_key_alias if api_key_alias is not None else (self.key_pool.all_aliases()[0] if self.key_pool.all_aliases() else None)
        api_key_value = None
        if alias is not None:
            key = self.key_pool.get_by_alias(alias)
            if key is None:
                raise ValueError(f"Unknown Gemini key alias '{alias}'. Available: {self.key_pool.all_aliases()}")
            api_key_value = key.value
        client = genai.Client(api_key=api_key_value) if api_key_value else genai.Client()
        return client, alias

    def _build_config(self, *, parameters: Optional[CallParameters], system_instruction: Optional[str], thinking_budget: Optional[int], include_thoughts: Optional[bool], structured_schema: Optional[type] = None, url_context: bool = False) -> Optional[types.GenerateContentConfig]:
        cfg_kwargs: Dict[str, Any] = {}
        if system_instruction is not None:
            cfg_kwargs["system_instruction"] = system_instruction
        if parameters is not None:
            if parameters.temperature is not None:
                cfg_kwargs["temperature"] = parameters.temperature
            # Note: add more fields (top_p, max_output_tokens) if/when supported; keeping minimal and safe
            if parameters.max_tokens is not None:
                cfg_kwargs["max_output_tokens"] = parameters.max_tokens
        if thinking_budget is not None or include_thoughts is not None:
            t_kwargs: Dict[str, Any] = {}
            if thinking_budget is not None:
                t_kwargs["thinking_budget"] = thinking_budget
            if include_thoughts is not None:
                t_kwargs["include_thoughts"] = include_thoughts
            cfg_kwargs["thinking_config"] = types.ThinkingConfig(**t_kwargs)
        if structured_schema is not None:
            # Gemini structured outputs via response_schema and JSON mime type
            cfg_kwargs["response_mime_type"] = "application/json"
            cfg_kwargs["response_schema"] = structured_schema
        if url_context:
            # Enable Gemini built-in URL context tool
            cfg_kwargs["tools"] = [{"url_context": {}}]
        if not cfg_kwargs:
            return None
        return types.GenerateContentConfig(**cfg_kwargs)

    @staticmethod
    def _get_field(obj: Any, key: str, default: Any = None) -> Any:
        if obj is None:
            return default
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    def call(self, *, model: str, contents: InputType, system_instruction: Optional[str] = None,
             parameters: Optional[CallParameters] = None, api_key_alias: Optional[str] = None,
             tags: Optional[List[str]] = None, call_id: Optional[str] = None,
             thinking_budget: Optional[int] = None, include_thoughts: Optional[bool] = None,
             structured_schema: Optional[type] = None, url_context: bool = False) -> Dict[str, Any]:
        client, used_alias = self._get_client(api_key_alias)
        record = self.manager.start_request("gemini", model, tags=tags, input_text=(contents if isinstance(contents, str) else None), call_id=call_id, api_key_alias=used_alias)
        started = time.perf_counter()
        try:
            cfg = self._build_config(parameters=parameters, system_instruction=system_instruction, thinking_budget=thinking_budget, include_thoughts=include_thoughts, structured_schema=structured_schema, url_context=url_context)
            kwargs: Dict[str, Any] = {"model": model, "contents": contents}
            if cfg is not None:
                kwargs["config"] = cfg

            resp = client.models.generate_content(**kwargs)

            latency_ms = int((time.perf_counter() - started) * 1000)

            usage = getattr(resp, "usage_metadata", None) or {}
            prompt_token_count = int(self._get_field(usage, "prompt_token_count", 0) or 0)
            cached_content_token_count = int(self._get_field(usage, "cached_content_token_count", 0) or 0)
            candidates_token_count = int(self._get_field(usage, "candidates_token_count", 0) or 0)
            thoughts_token_count = int(self._get_field(usage, "thoughts_token_count", 0) or 0)
            tool_use_prompt_token_count = int(self._get_field(usage, "tool_use_prompt_token_count", 0) or 0)

            billed_output = candidates_token_count + thoughts_token_count
            # Effective input should include tool-use prompt tokens when url_context/tools are used
            effective_input_tokens = prompt_token_count + tool_use_prompt_token_count

            output_text = getattr(resp, "text", None)
            response_text_len = len(output_text) if isinstance(output_text, str) else None

            self.manager.finalize_success(
                record,
                input_tokens=effective_input_tokens,
                cached_input_tokens=cached_content_token_count,
                output_tokens=billed_output,
                reasoning_tokens=thoughts_token_count,
                latency_ms=latency_ms,
                finish_reason=None,
                response_text_len=response_text_len,
                response_text=output_text,
            )

            return {
                "request_id": record.request_id,
                "call_id": record.call_id,
                "output_text": output_text,
                "output_parsed": getattr(resp, "parsed", None),
                "raw_response": resp,
            }
        except Exception as exc:
            self.manager.finalize_error(record, error_type=exc.__class__.__name__, message=str(exc))
            raise

    def call_stream(self, *, model: str, contents: InputType, system_instruction: Optional[str] = None,
                    parameters: Optional[CallParameters] = None, api_key_alias: Optional[str] = None,
                    tags: Optional[List[str]] = None, call_id: Optional[str] = None,
                    thinking_budget: Optional[int] = None, include_thoughts: Optional[bool] = None) -> Dict[str, Any]:
        client, used_alias = self._get_client(api_key_alias)
        record = self.manager.start_request("gemini", model, tags=tags, input_text=(contents if isinstance(contents, str) else None), call_id=call_id, api_key_alias=used_alias)
        started = time.perf_counter()
        ttft_ms: Optional[int] = None
        chunk_count = 0
        total_chunk_chars = 0
        output_text_parts: List[str] = []
        last_usage = None
        try:
            cfg = self._build_config(parameters=parameters, system_instruction=system_instruction, thinking_budget=thinking_budget, include_thoughts=include_thoughts)
            kwargs: Dict[str, Any] = {"model": model, "contents": contents}
            if cfg is not None:
                kwargs["config"] = cfg

            stream = client.models.generate_content_stream(**kwargs)
            for chunk in stream:
                if ttft_ms is None:
                    ttft_ms = int((time.perf_counter() - started) * 1000)
                chunk_count += 1
                text = getattr(chunk, "text", None)
                if isinstance(text, str) and text:
                    output_text_parts.append(text)
                    total_chunk_chars += len(text)
                    print(text, end="", flush=True)
                last_usage = getattr(chunk, "usage_metadata", last_usage)

            duration_ms = int((time.perf_counter() - started) * 1000)
            avg_chunk_chars = (total_chunk_chars / chunk_count) if chunk_count > 0 else None

            usage = last_usage or {}
            prompt_token_count = int(self._get_field(usage, "prompt_token_count", 0) or 0)
            cached_content_token_count = int(self._get_field(usage, "cached_content_token_count", 0) or 0)
            # For live streams, output tokens may be reported as response_token_count
            candidates_token_count = int(self._get_field(usage, "candidates_token_count", self._get_field(usage, "response_token_count", 0)) or 0)
            thoughts_token_count = int(self._get_field(usage, "thoughts_token_count", 0) or 0)
            tool_use_prompt_token_count = int(self._get_field(usage, "tool_use_prompt_token_count", 0) or 0)

            billed_output = candidates_token_count + thoughts_token_count
            effective_input_tokens = prompt_token_count + tool_use_prompt_token_count
            output_text = "".join(output_text_parts) if output_text_parts else None
            response_text_len = len(output_text) if isinstance(output_text, str) else None

            self.manager.finalize_success(
                record,
                input_tokens=effective_input_tokens,
                cached_input_tokens=cached_content_token_count,
                output_tokens=billed_output,
                reasoning_tokens=thoughts_token_count,
                latency_ms=duration_ms,
                ttft_ms=ttft_ms,
                stream_duration_ms=duration_ms,
                finish_reason=None,
                response_text_len=response_text_len,
                response_text=output_text,
                stream_chunk_count=chunk_count,
                stream_avg_chunk_chars=avg_chunk_chars,
            )

            return {
                "request_id": record.request_id,
                "call_id": record.call_id,
                "output_text": output_text,
                "raw_response": None,
            }
        except Exception as exc:
            self.manager.finalize_error(record, error_type=exc.__class__.__name__, message=str(exc))
            raise


