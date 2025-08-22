openai_models = [
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
  "gpt-4",
]

gemini_models = [
  "gemini-2.5-pro",
  "gemini-2.5-flash",
  "gemini-2.5-flash-lite",

  "gemini-2.0-flash",
  "gemini-2.0-flash-lite",

  "gemini-1.5-flash",
  "gemini-1.5-pro"
]

gemini_pricing = [
  {
    "model": "gemini-2.5-pro",
    "input_per_million_usd": { "<=200k_tokens": 1.25, ">200k_tokens": 2.50 },
    "cache_input_per_million_usd": { "<=200k_tokens": 0.31, ">200k_tokens": 0.625 },
    "output_per_million_usd": { "<=200k_tokens": 10.00, ">200k_tokens": 15.00 }
  },
  {
    "model": "gemini-2.5-flash",
    "input_per_million_usd": { "text_image_video": 0.30, "audio": 1.00 },
    "cache_input_per_million_usd": { "text_image_video": 0.075, "audio": 0.25 },
    "output_per_million_usd": 2.50
  },
  {
    "model": "gemini-2.5-flash-lite",
    "input_per_million_usd": { "text_image_video": 0.10, "audio": 0.30 },
    "cache_input_per_million_usd": { "text_image_video": 0.025, "audio": 0.125 },
    "output_per_million_usd": 0.40
  },
  {
    "model": "gemini-2.0-flash",
    "input_per_million_usd": { "text_image_video": 0.10, "audio": 0.70 },
    "cache_input_per_million_usd": { "text_image_video": 0.025, "audio": 0.175 },
    "output_per_million_usd": 0.40
  },
  {
    "model": "gemini-2.0-flash-lite",
    "input_per_million_usd": 0.075,
    "cache_input_per_million_usd": null,
    "output_per_million_usd": 0.30,
    "notes": "Context caching not available"
  },
  {
    "model": "gemini-1.5-flash",
    "input_per_million_usd": { "<=128k_tokens": 0.075, ">128k_tokens": 0.15 },
    "cache_input_per_million_usd": { "<=128k_tokens": 0.01875, ">128k_tokens": 0.0375 },
    "output_per_million_usd": { "<=128k_tokens": 0.30, ">128k_tokens": 0.60 }
  },
  {
    "model": "gemini-1.5-pro",
    "input_per_million_usd": { "<=128k_tokens": 1.25, ">128k_tokens": 2.50 },
    "cache_input_per_million_usd": { "<=128k_tokens": 0.3125, ">128k_tokens": 0.625 },
    "output_per_million_usd": { "<=128k_tokens": 5.00, ">128k_tokens": 10.00 }
  }
]

openai_pricing = [
  {"model": "gpt-5", "input_per_million_usd": 1.25, "cached_input_per_million_usd": 0.125, "output_per_million_usd": 10.0},
  {"model": "gpt-5-mini", "input_per_million_usd": 0.25, "cached_input_per_million_usd": 0.025, "output_per_million_usd": 2.0},
  {"model": "gpt-5-nano", "input_per_million_usd": 0.05, "cached_input_per_million_usd": 0.005, "output_per_million_usd": 0.4},
  {"model": "gpt-5-chat-latest", "input_per_million_usd": 1.25, "cached_input_per_million_usd": 0.125, "output_per_million_usd": 10.0},

  {"model": "o3", "input_per_million_usd": 2.0, "cached_input_per_million_usd": 0.5, "output_per_million_usd": 8.0},
  {"model": "o3-mini", "input_per_million_usd": 1.1, "cached_input_per_million_usd": 0.55, "output_per_million_usd": 4.4},
  {"model": "o3-deep-research", "input_per_million_usd": 10.0, "cached_input_per_million_usd": 2.5, "output_per_million_usd": 40.0},

  {"model": "o4-mini", "input_per_million_usd": 1.1, "cached_input_per_million_usd": 0.275, "output_per_million_usd": 4.4},
  {"model": "o4-mini-deep-research", "input_per_million_usd": 2.0, "cached_input_per_million_usd": 0.5, "output_per_million_usd": 8.0},

  {"model": "gpt-4.1", "input_per_million_usd": 2.0, "cached_input_per_million_usd": 0.5, "output_per_million_usd": 8.0},
  {"model": "gpt-4.1-mini", "input_per_million_usd": 0.4, "cached_input_per_million_usd": 0.1, "output_per_million_usd": 1.6},

  {"model": "gpt-4o", "input_per_million_usd": 5.0, "cached_input_per_million_usd": 2.5, "output_per_million_usd": 20.0},
  {"model": "gpt-4o-mini", "input_per_million_usd": 0.6, "cached_input_per_million_usd": 0.3, "output_per_million_usd": 2.4},

  {"model": "gpt-4", "input_per_million_usd": 30.0, "cached_input_per_million_usd": null, "output_per_million_usd": 60.0}
]
