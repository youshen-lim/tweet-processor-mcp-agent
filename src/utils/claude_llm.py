"""
Claude LLM wrapper for the MCP agents.

mcp-agent's AnthropicAugmentedLLM.generate_str() hides the API response, so it
cannot tell a refusal or a max_tokens cut-off from a normal answer, and it never
records token usage. ClaudeLLM keeps the same generate_str() interface and adds:

  1. Model-aware thinking / effort settings (Claude Sonnet 5.5 runs adaptive
     thinking by default and rejects {"type": "disabled"}; Sonnet 4.5 accepts
     neither "between_tools" nor an effort level).
  2. Refusal, truncation, and empty-response detection, raised as LLMCallError.
  3. One JSON line per API call in logs/token_usage.jsonl (override the path with
     the TOKEN_USAGE_LOG environment variable), with an estimated USD cost.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp_agent.workflows.llm.augmented_llm import RequestParams
from mcp_agent.workflows.llm.augmented_llm_anthropic import AnthropicAugmentedLLM

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_USAGE_LOG = PROJECT_ROOT / "logs" / "token_usage.jsonl"

# USD per million tokens, Claude API list prices
# (https://platform.claude.com/docs/en/about-claude/pricing, checked 2026-10-01).
PRICING = {
    "claude-sonnet-5-5": {"input": 2.00, "output": 10.00, "cache_write": 2.50, "cache_read": 0.20},
    "claude-sonnet-5": {"input": 2.00, "output": 10.00, "cache_write": 2.50, "cache_read": 0.20},
    "claude-sonnet-4-5-20250929": {"input": 3.00, "output": 15.00, "cache_write": 3.75, "cache_read": 0.30},
}

# Models that take {"type": "between_tools"} as the lowest thinking setting.
# It is accepted at low, medium, and high effort only.
BETWEEN_TOOLS_MODELS = ("claude-sonnet-5-5",)

# Key in RequestParams.metadata that callers use to ask for an effort level.
# ClaudeLLM translates it per model and never sends it to the API as-is.
EFFORT_KEY = "effort"


class LLMCallError(Exception):
    """The API call finished but produced no usable answer."""

    def __init__(self, message: str, stop_reason: Optional[str] = None, details: Any = None):
        super().__init__(message)
        self.stop_reason = stop_reason
        self.details = details


def claude_request_params(max_tokens: int, effort: str = "medium") -> RequestParams:
    """
    Build per-call RequestParams for a single-shot, tool-free request.

    max_iterations=1 matters: mcp-agent treats any stop_reason it does not know
    (such as "refusal") as tool use and loops again, which would resend the
    conversation ending on an assistant turn (a prefill, which Sonnet 5.5 rejects).
    """
    return RequestParams(
        maxTokens=max_tokens,
        max_iterations=1,
        metadata={EFFORT_KEY: effort},
    )


def thinking_overrides(model: str, effort: Optional[str]) -> Dict[str, Any]:
    """API arguments that set thinking and effort for the given model."""
    if model.startswith(BETWEEN_TOOLS_MODELS):
        return {
            "thinking": {"type": "between_tools"},
            "output_config": {"effort": effort or "medium"},
        }
    # Sonnet 4.5: no thinking unless requested, and no effort parameter.
    return {}


def estimate_cost_usd(model: str, usage: Dict[str, int]) -> Optional[float]:
    """Estimated list-price cost of one call, or None for an unpriced model."""
    prices = next((p for name, p in PRICING.items() if model.startswith(name)), None)
    if prices is None:
        return None
    cost = (
        usage.get("input_tokens", 0) * prices["input"]
        + usage.get("output_tokens", 0) * prices["output"]
        + usage.get("cache_creation_input_tokens", 0) * prices["cache_write"]
        + usage.get("cache_read_input_tokens", 0) * prices["cache_read"]
    ) / 1_000_000
    return round(cost, 6)


def log_usage(record: Dict[str, Any]) -> None:
    """Append one usage record to the JSONL log. Never raises."""
    path = Path(os.getenv("TOKEN_USAGE_LOG", str(DEFAULT_USAGE_LOG)))
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except OSError as e:
        print(f"⚠️  Could not write token usage log ({e})")


class ClaudeLLM(AnthropicAugmentedLLM):
    """AnthropicAugmentedLLM with model-aware thinking, refusal checks, and usage logging."""

    @property
    def model(self) -> str:
        """The model this LLM sends requests to (from mcp_agent.config.yaml unless overridden)."""
        return self.default_request_params.model

    async def generate_str(self, message, request_params: RequestParams | None = None) -> str:
        params = self.get_request_params(request_params)
        model = params.model or self.model
        metadata = dict(params.metadata or {})
        effort = metadata.pop(EFFORT_KEY, None)
        metadata.update(thinking_overrides(model, effort))
        params.metadata = metadata or None

        responses: List[Any] = await self.generate(message=message, request_params=params)
        if not responses:
            raise LLMCallError(f"No response from {model} (the API call failed; see the mcp-agent log)")

        for response in responses:
            self._record_usage(response, model)

        final = responses[-1]
        stop_reason = getattr(final, "stop_reason", None)
        if stop_reason == "refusal":
            details = getattr(final, "stop_details", None)
            category = getattr(details, "category", None) if details else None
            raise LLMCallError(
                f"{model} declined the request (refusal category: {category or 'unspecified'})",
                stop_reason=stop_reason,
                details=details,
            )
        if stop_reason == "max_tokens":
            raise LLMCallError(
                f"{model} hit max_tokens ({params.maxTokens}); the response was cut off",
                stop_reason=stop_reason,
            )

        text = "\n".join(
            block.text for block in final.content if getattr(block, "type", None) == "text"
        )
        if not text.strip():
            raise LLMCallError(f"{model} returned no text (stop_reason: {stop_reason})", stop_reason=stop_reason)
        return text

    def _record_usage(self, response: Any, requested_model: str) -> None:
        usage_obj = getattr(response, "usage", None)
        usage = {
            key: getattr(usage_obj, key, None) or 0
            for key in (
                "input_tokens",
                "output_tokens",
                "cache_creation_input_tokens",
                "cache_read_input_tokens",
            )
        }
        model = getattr(response, "model", None) or requested_model
        cost = estimate_cost_usd(model, usage)
        log_usage({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "agent": self.agent.name if self.agent else self.name,
            "model": model,
            "stop_reason": getattr(response, "stop_reason", None),
            **usage,
            "estimated_cost_usd": cost,
            "message_id": getattr(response, "id", None),
        })
        cost_str = f", ~${cost:.4f}" if cost is not None else ""
        print(f"📊 Tokens: {usage['input_tokens']} in / {usage['output_tokens']} out ({model}{cost_str})")
