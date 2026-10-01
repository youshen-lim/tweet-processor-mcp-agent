"""
Tests for src/utils/claude_llm.py: per-model thinking settings, cost estimates,
usage logging, and refusal / truncation / empty-response detection.
"""

import json
import os
import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.claude_llm import (  # noqa: E402
    ClaudeLLM,
    LLMCallError,
    claude_request_params,
    estimate_cost_usd,
    log_usage,
    thinking_overrides,
)


def _response(text="Tweet text", stop_reason="end_turn", stop_details=None):
    return SimpleNamespace(
        content=[SimpleNamespace(type="text", text=text)] if text is not None else [],
        stop_reason=stop_reason,
        stop_details=stop_details,
        model="claude-sonnet-5-5",
        id="msg_test",
        usage=SimpleNamespace(input_tokens=100, output_tokens=20,
                              cache_creation_input_tokens=0, cache_read_input_tokens=0),
    )


def _stub_llm(responses, model="claude-sonnet-5-5"):
    """Minimal stand-in carrying just what ClaudeLLM.generate_str touches."""
    return SimpleNamespace(
        model=model,
        get_request_params=lambda rp: rp,
        generate=AsyncMock(return_value=responses),
        _record_usage=MagicMock(),
    )


class TestThinkingOverrides:
    def test_sonnet_5_5_uses_between_tools_and_effort(self):
        assert thinking_overrides("claude-sonnet-5-5", "low") == {
            "thinking": {"type": "between_tools"},
            "output_config": {"effort": "low"},
        }

    def test_sonnet_4_5_gets_no_thinking_or_effort(self):
        assert thinking_overrides("claude-sonnet-4-5-20250929", "medium") == {}

    def test_request_params_are_single_shot(self):
        params = claude_request_params(max_tokens=1024, effort="medium")
        assert params.max_iterations == 1
        assert params.maxTokens == 1024
        assert params.metadata == {"effort": "medium"}


class TestCostEstimate:
    def test_sonnet_5_5_list_price(self):
        usage = {"input_tokens": 1_000_000, "output_tokens": 100_000}
        assert estimate_cost_usd("claude-sonnet-5-5", usage) == pytest.approx(3.0)

    def test_sonnet_4_5_list_price(self):
        usage = {"input_tokens": 1_000_000, "output_tokens": 100_000}
        assert estimate_cost_usd("claude-sonnet-4-5-20250929", usage) == pytest.approx(4.5)

    def test_unknown_model_is_unpriced(self):
        assert estimate_cost_usd("some-other-model", {"input_tokens": 10}) is None


class TestUsageLog:
    def test_appends_json_line(self, tmp_path, monkeypatch):
        log_file = tmp_path / "usage.jsonl"
        monkeypatch.setenv("TOKEN_USAGE_LOG", str(log_file))
        log_usage({"model": "claude-sonnet-5-5", "input_tokens": 5})
        log_usage({"model": "claude-sonnet-5-5", "input_tokens": 6})
        lines = log_file.read_text(encoding="utf-8").splitlines()
        assert [json.loads(line)["input_tokens"] for line in lines] == [5, 6]


class TestGenerateStr:
    @pytest.mark.asyncio
    async def test_returns_text_and_sends_model_settings(self):
        llm = _stub_llm([_response("AI drives value 🚀")])
        text = await ClaudeLLM.generate_str(llm, "prompt", claude_request_params(1024, "low"))

        assert text == "AI drives value 🚀"
        sent = llm.generate.await_args.kwargs["request_params"]
        assert sent.metadata == {"thinking": {"type": "between_tools"}, "output_config": {"effort": "low"}}
        llm._record_usage.assert_called_once()

    @pytest.mark.asyncio
    async def test_sonnet_4_5_request_carries_no_effort(self):
        llm = _stub_llm([_response()], model="claude-sonnet-4-5-20250929")
        await ClaudeLLM.generate_str(llm, "prompt", claude_request_params(1024, "medium"))
        assert llm.generate.await_args.kwargs["request_params"].metadata is None

    @pytest.mark.asyncio
    async def test_refusal_raises_with_category(self):
        details = SimpleNamespace(category="frontier_llm", explanation="...")
        llm = _stub_llm([_response(None, stop_reason="refusal", stop_details=details)])
        with pytest.raises(LLMCallError, match="frontier_llm") as exc:
            await ClaudeLLM.generate_str(llm, "prompt", claude_request_params(1024))
        assert exc.value.stop_reason == "refusal"
        llm._record_usage.assert_called_once()  # refusals are still billed and logged

    @pytest.mark.asyncio
    async def test_max_tokens_raises(self):
        llm = _stub_llm([_response('{"key_insights": [', stop_reason="max_tokens")])
        with pytest.raises(LLMCallError, match="max_tokens"):
            await ClaudeLLM.generate_str(llm, "prompt", claude_request_params(64))

    @pytest.mark.asyncio
    async def test_empty_text_raises(self):
        llm = _stub_llm([_response("   ")])
        with pytest.raises(LLMCallError, match="no text"):
            await ClaudeLLM.generate_str(llm, "prompt", claude_request_params(1024))

    @pytest.mark.asyncio
    async def test_failed_call_raises(self):
        llm = _stub_llm([])
        with pytest.raises(LLMCallError, match="No response"):
            await ClaudeLLM.generate_str(llm, "prompt", claude_request_params(1024))
