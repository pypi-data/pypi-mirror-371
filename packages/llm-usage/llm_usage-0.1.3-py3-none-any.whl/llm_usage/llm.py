from __future__ import annotations

class LLM:

    def __init__(self, openai_api_keys: list[str], gemini_api_keys: list[str], log_dir: str):

        self.open_api_keys = openai_api_keys
        self.gemini_api_keys = gemini_api_keys

        self.total_inputs_tokens = 0
        self.total_reasoning_tokens = 0
        # Output + Reasoning
        self.total_output_tokens = 0

        self.total_input_cost = 0
        self.total_output_cost = 0

        self.average_latency = 0
        self.log_dir = log_dir
        # Lazy inits for manager/providers to avoid importing at module load
        self._manager = None
        self._openai_provider = None
        self._gemini_provider = None
        self._openai_keypool = None
        self._gemini_keypool = None

    def log_result(self):
        pass

    def call_openai_model(self):
        pass

    def call_openai_stream_model(self):
        pass

    def call_gemini_model(self):
        pass

    def call_gemini_stream_model(self):
        pass

    def call_model(self, *, model: str, input_or_contents, instructions: str | None = None,
                   parameters=None, api_key_alias: str | None = None, tags: list[str] | None = None,
                   thinking_budget: int | None = None, include_thoughts: bool | None = None,
                   call_id: str | None = None,
                   structured_schema: type | None = None,
                   url_context: bool = False,
                   fallback_plan: list[dict] | None = None):
        from core.router import validate_and_route
        from core.manager import LLMCallManager
        from core.keys import KeyPool
        from core.models import get_provider_for_model
        from providers.openai_provider import OpenAIProvider
        from providers.gemini_provider import GeminiProvider
        from core.router import execute_with_fallback

        provider, _ = validate_and_route(model)
        if self._manager is None:
            self._manager = LLMCallManager(db_path=f"{self.log_dir}/llm.sqlite")
        # Auto-generate a call_id for direct calls without fallback, for grouping
        if not call_id:
            import uuid
            call_id = uuid.uuid4().hex
        if fallback_plan:
            if self._manager is None:
                self._manager = LLMCallManager(db_path=f"{self.log_dir}/llm.sqlite")
            # Prepare providers and keypools
            if self._openai_keypool is None:
                self._openai_keypool = KeyPool.from_values(self.open_api_keys, prefix="openai")
            if self._gemini_keypool is None:
                self._gemini_keypool = KeyPool.from_values(self.gemini_api_keys, prefix="gemini")
            if self._openai_provider is None:
                self._openai_provider = OpenAIProvider(manager=self._manager, key_pool=self._openai_keypool)
            if self._gemini_provider is None:
                self._gemini_provider = GeminiProvider(manager=self._manager, key_pool=self._gemini_keypool)

            steps = []
            for step in fallback_plan:
                step_model = step["model"]
                step_provider, _ = validate_and_route(step_model)
                key_aliases = step.get("key_aliases")
                if step_provider == "openai":
                    def mk_exec(m=step_model, ia=api_key_alias):
                        def _exec(record):
                            try:
                                res = self._openai_provider.call(model=m, input=input_or_contents, instructions=instructions, parameters=parameters, api_key_alias=record.api_key_alias, tags=tags, call_id=record.call_id, structured_schema=structured_schema)
                                return True, None
                            except Exception as e:
                                return False, str(e)
                        return _exec
                    steps.append(("openai", step_model, key_aliases, mk_exec()))
                else:
                    def mk_exec(m=step_model, ia=api_key_alias):
                        def _exec(record):
                            try:
                                res = self._gemini_provider.call(model=m, contents=input_or_contents, system_instruction=instructions, parameters=parameters, api_key_alias=record.api_key_alias, tags=tags, call_id=record.call_id, thinking_budget=thinking_budget, include_thoughts=include_thoughts, structured_schema=structured_schema, url_context=url_context)
                                return True, None
                            except Exception as e:
                                return False, str(e)
                        return _exec
                    steps.append(("gemini", step_model, key_aliases, mk_exec()))

            ok, request_id, used_call_id = execute_with_fallback(manager=self._manager, steps=steps, tags=tags, input_text=(input_or_contents if isinstance(input_or_contents, str) else None))
            return {"success": ok, "request_id": request_id, "call_id": used_call_id}

        if provider == "openai":
            if self._openai_keypool is None:
                self._openai_keypool = KeyPool.from_values(self.open_api_keys, prefix="openai")
            if self._openai_provider is None:
                self._openai_provider = OpenAIProvider(manager=self._manager, key_pool=self._openai_keypool)
            return self._openai_provider.call(
                model=model,
                input=input_or_contents,
                instructions=instructions,
                parameters=parameters,
                api_key_alias=api_key_alias,
                tags=tags,
                call_id=call_id,
                structured_schema=structured_schema,
            )
        elif provider == "gemini":
            if self._gemini_keypool is None:
                self._gemini_keypool = KeyPool.from_values(self.gemini_api_keys, prefix="gemini")
            if self._gemini_provider is None:
                self._gemini_provider = GeminiProvider(manager=self._manager, key_pool=self._gemini_keypool)
            return self._gemini_provider.call(
                model=model,
                contents=input_or_contents,
                system_instruction=instructions,
                parameters=parameters,
                api_key_alias=api_key_alias,
                tags=tags,
                call_id=call_id,
                thinking_budget=thinking_budget,
                include_thoughts=include_thoughts,
                url_context=url_context,
                structured_schema=structured_schema,
            )
        else:
            raise ValueError("Unsupported provider")

    def call_stream_model(self, *, model: str, input_or_contents, instructions: str | None = None,
                          parameters=None, api_key_alias: str | None = None, tags: list[str] | None = None,
                          thinking_budget: int | None = None, include_thoughts: bool | None = None,
                          call_id: str | None = None,
                          fallback_plan: list[dict] | None = None):
        from core.router import validate_and_route
        from core.manager import LLMCallManager
        from core.keys import KeyPool
        from providers.openai_provider import OpenAIProvider
        from providers.gemini_provider import GeminiProvider
        from core.router import execute_with_fallback

        provider, _ = validate_and_route(model)
        if self._manager is None:
            self._manager = LLMCallManager(db_path=f"{self.log_dir}/llm.sqlite")
        if not call_id:
            import uuid
            call_id = uuid.uuid4().hex
        if fallback_plan:
            if self._openai_keypool is None:
                self._openai_keypool = KeyPool.from_values(self.open_api_keys, prefix="openai")
            if self._gemini_keypool is None:
                self._gemini_keypool = KeyPool.from_values(self.gemini_api_keys, prefix="gemini")
            if self._openai_provider is None:
                self._openai_provider = OpenAIProvider(manager=self._manager, key_pool=self._openai_keypool)
            if self._gemini_provider is None:
                self._gemini_provider = GeminiProvider(manager=self._manager, key_pool=self._gemini_keypool)

            steps = []
            for step in fallback_plan:
                step_model = step["model"]
                step_provider, _ = validate_and_route(step_model)
                key_aliases = step.get("key_aliases")
                if step_provider == "openai":
                    def mk_exec(m=step_model):
                        def _exec(record):
                            try:
                                res = self._openai_provider.call_stream(model=m, input=input_or_contents, instructions=instructions, parameters=parameters, api_key_alias=record.api_key_alias, tags=tags, call_id=record.call_id)
                                return True, None
                            except Exception as e:
                                return False, str(e)
                        return _exec
                    steps.append(("openai", step_model, key_aliases, mk_exec()))
                else:
                    def mk_exec(m=step_model):
                        def _exec(record):
                            try:
                                res = self._gemini_provider.call_stream(model=m, contents=input_or_contents, system_instruction=instructions, parameters=parameters, api_key_alias=record.api_key_alias, tags=tags, call_id=record.call_id, thinking_budget=thinking_budget, include_thoughts=include_thoughts)
                                return True, None
                            except Exception as e:
                                return False, str(e)
                        return _exec
                    steps.append(("gemini", step_model, key_aliases, mk_exec()))

            ok, request_id, used_call_id = execute_with_fallback(manager=self._manager, steps=steps, tags=tags, input_text=(input_or_contents if isinstance(input_or_contents, str) else None))
            return {"success": ok, "request_id": request_id, "call_id": used_call_id}

        if provider == "openai":
            if self._openai_keypool is None:
                self._openai_keypool = KeyPool.from_values(self.open_api_keys, prefix="openai")
            if self._openai_provider is None:
                self._openai_provider = OpenAIProvider(manager=self._manager, key_pool=self._openai_keypool)
            return self._openai_provider.call_stream(
                model=model,
                input=input_or_contents,
                instructions=instructions,
                parameters=parameters,
                api_key_alias=api_key_alias,
                tags=tags,
                call_id=call_id,
            )
        elif provider == "gemini":
            if self._gemini_keypool is None:
                self._gemini_keypool = KeyPool.from_values(self.gemini_api_keys, prefix="gemini")
            if self._gemini_provider is None:
                self._gemini_provider = GeminiProvider(manager=self._manager, key_pool=self._gemini_keypool)
            return self._gemini_provider.call_stream(
                model=model,
                contents=input_or_contents,
                system_instruction=instructions,
                parameters=parameters,
                api_key_alias=api_key_alias,
                tags=tags,
                call_id=call_id,
                thinking_budget=thinking_budget,
                include_thoughts=include_thoughts,
            )
        else:
            raise ValueError("Unsupported provider")


