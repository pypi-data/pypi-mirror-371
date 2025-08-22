# llm-usage

A lightweight toolkit to call OpenAI and Gemini models while automatically logging usage (tokens), costs, latency, errors/retries, streaming diagnostics, and more — plus a built-in dashboard for browsing, filtering, rerunning requests, and inspecting inputs/outputs.

## Features

- Provider-agnostic logging across OpenAI and Gemini
- Per-call metadata: tags, parameters (temperature, top_p, max tokens), model/provider
- Token accounting: input, cached input, output, reasoning tokens (when available)
- Cost computation: per-million token pricing with cached input pricing
- Latency metrics: total latency, time-to-first-token (TTFT), stream duration, chunk stats
- Errors/retries and cross-provider fallback support
- API-key-aware fallback within provider steps
- Streaming support for both providers with live console printing
- SQLite storage with an inspectable schema
- Beautiful dashboard (FastAPI + Jinja2): filtering, totals, details, input/output view, and rerun
- Simple Python API and CLI commands

## Install

```
pip install llm-usage
```

From source (editable):

```
pip install -e .
```

## Environment

- OPENAI_API_KEYS: comma-separated OpenAI keys (e.g. `sk-aaa,sk-bbb`)
- GEMINI_API_KEYS: comma-separated Gemini keys (e.g. `g-aaa,g-bbb`)
- LLM_LOG_DIR: directory to store logs/SQLite (default: `./logs`)

## CLI

- Start the dashboard:

```
llm-usage-dashboard
# then open http://127.0.0.1:8000
```

- Run sample calls:

```
llm-usage-samples
```

## Python API

Import the main APIs from the package:

```
from llm_usage import LLM, CallParameters

llm = LLM(
  openai_api_keys=["sk-..."],
  gemini_api_keys=["g-..."],
  log_dir="./logs",
)

res = llm.call_model(
  model="gpt-5-mini",
  input_or_contents="Write a two-line poem about monsoons.",
  parameters=CallParameters(temperature=0.2, max_tokens=200),
  api_key_alias="openai-0",
  tags=["demo", "poem"],
)
print(res["output_text"])  # response string
```

### Streaming

```
res = llm.call_stream_model(
  model="gemini-2.5-flash",
  input_or_contents=["Explain how AI works"],
  instructions="Stream the response.",
  api_key_alias="gemini-0",
  tags=["demo", "stream"],
)
# chunks print live to stdout; res includes final request_id/call_id
```

### Generation parameters (temperature, top_p, max tokens)

```
from llm_usage import CallParameters

# OpenAI example
res = llm.call_model(
  model="gpt-5-mini",
  input_or_contents="Write a two-line limerick about rain.",
  parameters=CallParameters(temperature=0.2, top_p=0.9, max_tokens=120),
  api_key_alias="openai-0",
  tags=["demo", "params"],
)
print(res["output_text"]) 

# Gemini example (temperature and max tokens are supported via config)
res = llm.call_model(
  model="gemini-2.5-flash",
  input_or_contents="Summarize monsoons in one paragraph.",
  parameters=CallParameters(temperature=0.3, max_tokens=180),
  api_key_alias="gemini-0",
  tags=["demo", "params"],
)
print(res["output_text"]) 
```

### Gemini thinking and thought summaries

Gemini 2.5 models support a thinking budget and optional thought summaries. You can reduce latency by setting `thinking_budget=0`, or enable summaries with `include_thoughts=True`.

```
# Disable thinking for faster responses
res = llm.call_model(
  model="gemini-2.5-flash",
  input_or_contents="How does AI work?",
  api_key_alias="gemini-0",
  thinking_budget=0,               # disable thinking
  tags=["demo", "thinking"],
)

# Enable thought summaries (returned tokens counted in usage)
res = llm.call_model(
  model="gemini-2.5-pro",
  input_or_contents="What is the sum of the first 50 prime numbers?",
  api_key_alias="gemini-0",
  thinking_budget=-1,              # dynamic
  include_thoughts=True,
  tags=["demo", "thinking"],
)
print(res["output_text"]) 
```

### Structured outputs

Use `structured_schema` to request typed outputs. Define Pydantic models and pass them with your call. The parsed result is returned in `res["output_parsed"]`.

OpenAI example:

```
from pydantic import BaseModel

class CalendarEvent(BaseModel):
  name: str
  date: str
  participants: list[str]

res = llm.call_model(
  model="gpt-5-mini",
  input_or_contents=[
    {"role": "system", "content": "Extract the event information."},
    {"role": "user", "content": "Alice and Bob are going to a science fair on Friday."},
  ],
  structured_schema=CalendarEvent,
  api_key_alias="openai-0",
  tags=["demo", "structured"],
)
print(res["output_parsed"])  # CalendarEvent(...)
```

Gemini example:

```
from pydantic import BaseModel

class Recipe(BaseModel):
  recipe_name: str
  ingredients: list[str]

res = llm.call_model(
  model="gemini-2.5-flash",
  input_or_contents="List a few popular cookie recipes, and include the amounts of ingredients.",
  structured_schema=list[Recipe],   # or Recipe for single-object outputs
  api_key_alias="gemini-0",
  tags=["demo", "structured"],
)
print(res["output_parsed"])  # List[Recipe]
```

Note: On Gemini, Pydantic validation errors may be suppressed by the underlying client; `.parsed` may be empty/null if the output cannot be validated. The raw JSON string is still available via `res["output_text"]`.

### Gemini URL context tool

To allow Gemini to fetch and ground on URLs mentioned in your prompt, enable the built-in URL context tool by setting `url_context=True`:

```
res = llm.call_model(
  model="gemini-2.5-flash",
  input_or_contents="What are the top 3 recent announcements from the Gemini API according to https://ai.google.dev/gemini-api/docs/changelog",
  api_key_alias="gemini-0",
  url_context=True,
  thinking_budget=0,
  tags=["demo", "url-context"],
)
print(res["output_text"]) 
```

### Fallback across models/providers

Provide a fallback plan as a list of steps with model and optional key aliases. Each step is attempted in order; on failure, it proceeds to the next.

```
plan = [
  {"model": "gpt-5-mini", "key_aliases": ["openai-0", "openai-1"]},
  {"model": "gemini-2.5-pro", "key_aliases": ["gemini-0"]},
]
res = llm.call_model(
  model="gpt-5-mini",
  input_or_contents="Say 'fallback test ok'",
  tags=["demo", "fallback"],
  fallback_plan=plan,
)
print(res)  # { success, request_id, call_id }
```

## Dashboard

The dashboard reads from the SQLite DB in `LLM_LOG_DIR/llm.sqlite`.

- Filters: provider, model, tag, success, date range
- Summary: total requests, total cost, average latency
- Table: time, provider, model, tags, latency, tokens, cost, status, details link
- Details: pretty metadata JSON, input and output text, latencies, tokens, costs, rerun button

## Data model (high level)

- Request record fields (subset):
  - identifiers: `request_id`, `call_id`, timestamps
  - classification: `provider`, `model`, `api_key_alias`, `tags`
  - tokens: `input_tokens`, `cached_input_tokens`, `output_tokens`, `reasoning_tokens`
  - costs: `input_cost_usd`, `cached_input_cost_usd`, `output_cost_usd`, `reasoning_cost_usd`, `total_cost_usd`
  - latency: `latency_ms`, `ttft_ms`, `stream_duration_ms`, stream chunk stats
  - results: `response_text`, `response_text_len`, `finish_reason`, `success`
  - errors/rate limit: `error_json`, `rate_limit_json`, `retry_count`

## Pricing notes

- Costs are calculated per 1M tokens (USD) using a built-in pricing table derived from your config in `src/utils/llm-models.py`.
- Billed formula examples:
  - OpenAI: `uncached_input * input_rate + cached_input * cached_rate + output * output_rate`
  - Gemini (Responses API): `output = candidates + thoughts`; cached input billed separately

## Tips

- API key aliases are created automatically (`openai-0`, `gemini-0`, ...). You can specify which alias to use per call.
- For streaming, the SDK prints chunks to stdout as they arrive; the final usage is recorded in the database.
- Each direct call gets a generated `call_id`. Fallback attempts share the same `call_id` for aggregation.
