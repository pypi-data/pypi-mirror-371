from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass(frozen=True)
class Pricing:
    # prices per 1M tokens in USD
    input_per_1m: float
    output_per_1m: float
    reasoning_per_1m: float = 0.0
    cached_input_per_1m: float = 0.0

    def compute_cost(self, *, input_tokens: int, output_tokens: int, reasoning_tokens: int = 0, cached_input_tokens: int = 0) -> Dict[str, float]:
        denom = 1_000_000.0
        input_cost = (input_tokens / denom) * self.input_per_1m
        cached_input_cost = (cached_input_tokens / denom) * self.cached_input_per_1m
        output_cost = (output_tokens / denom) * self.output_per_1m
        reasoning_cost = (reasoning_tokens / denom) * self.reasoning_per_1m
        total = input_cost + cached_input_cost + output_cost + reasoning_cost
        return {
            "input_cost_usd": round(input_cost, 6),
            "cached_input_cost_usd": round(cached_input_cost, 6),
            "output_cost_usd": round(output_cost, 6),
            "reasoning_cost_usd": round(reasoning_cost, 6),
            "total_cost_usd": round(total, 6),
        }


# Central pricing tables, per 1M tokens, USD (from utils lists)
PRICING_TABLE: Dict[str, Pricing] = {
    # OpenAI
    "gpt-5": Pricing(input_per_1m=1.25, output_per_1m=10.0, cached_input_per_1m=0.125),
    "gpt-5-mini": Pricing(input_per_1m=0.25, output_per_1m=2.0, cached_input_per_1m=0.025),
    "gpt-5-nano": Pricing(input_per_1m=0.05, output_per_1m=0.4, cached_input_per_1m=0.005),
    "gpt-5-chat-latest": Pricing(input_per_1m=1.25, output_per_1m=10.0, cached_input_per_1m=0.125),
    "o3": Pricing(input_per_1m=2.0, output_per_1m=8.0, cached_input_per_1m=0.5),
    "o3-mini": Pricing(input_per_1m=1.1, output_per_1m=4.4, cached_input_per_1m=0.55),
    "o3-deep-research": Pricing(input_per_1m=10.0, output_per_1m=40.0, cached_input_per_1m=2.5),
    "o4-mini": Pricing(input_per_1m=1.1, output_per_1m=4.4, cached_input_per_1m=0.275),
    "o4-mini-deep-research": Pricing(input_per_1m=2.0, output_per_1m=8.0, cached_input_per_1m=0.5),
    "gpt-4.1": Pricing(input_per_1m=2.0, output_per_1m=8.0, cached_input_per_1m=0.5),
    "gpt-4.1-mini": Pricing(input_per_1m=0.4, output_per_1m=1.6, cached_input_per_1m=0.1),
    "gpt-4o": Pricing(input_per_1m=5.0, output_per_1m=20.0, cached_input_per_1m=2.5),
    "gpt-4o-mini": Pricing(input_per_1m=0.6, output_per_1m=2.4, cached_input_per_1m=0.3),
    "gpt-4": Pricing(input_per_1m=30.0, output_per_1m=60.0, cached_input_per_1m=0.0),

    # Gemini (baseline tiers)
    "gemini-2.5-pro": Pricing(input_per_1m=1.25, output_per_1m=10.0, cached_input_per_1m=0.31),
    "gemini-2.5-flash": Pricing(input_per_1m=0.30, output_per_1m=2.50, cached_input_per_1m=0.075),
    "gemini-2.5-flash-lite": Pricing(input_per_1m=0.10, output_per_1m=0.40, cached_input_per_1m=0.025),
    "gemini-2.0-flash": Pricing(input_per_1m=0.10, output_per_1m=0.40, cached_input_per_1m=0.025),
    "gemini-2.0-flash-lite": Pricing(input_per_1m=0.075, output_per_1m=0.30, cached_input_per_1m=0.0),
    "gemini-1.5-flash": Pricing(input_per_1m=0.075, output_per_1m=0.30, cached_input_per_1m=0.01875),
    "gemini-1.5-pro": Pricing(input_per_1m=1.25, output_per_1m=5.0, cached_input_per_1m=0.3125),
}


def compute_costs_for_model(model: str, input_tokens: int, output_tokens: int, reasoning_tokens: int = 0, cached_input_tokens: int = 0) -> Dict[str, float]:
    pricing = PRICING_TABLE.get(model)
    if pricing is None:
        # Unknown model -> zero cost to avoid surprises; caller can override.
        return {
            "input_cost_usd": 0.0,
            "cached_input_cost_usd": 0.0,
            "output_cost_usd": 0.0,
            "reasoning_cost_usd": 0.0,
            "total_cost_usd": 0.0,
        }
    return pricing.compute_cost(input_tokens=input_tokens, output_tokens=output_tokens, reasoning_tokens=reasoning_tokens, cached_input_tokens=cached_input_tokens)


