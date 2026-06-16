"""
Unit tests for optional source context helpers.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.source_context import MAX_SOURCE_CONTEXT_CHARS, load_optional_source_context


@pytest.mark.unit
class TestSourceContext:
    """Test optional source context loading."""

    def test_empty_source_context_path_returns_empty_string(self):
        """Test missing optional source context configuration."""
        assert load_optional_source_context(None) == ""
        assert load_optional_source_context("") == ""
        assert load_optional_source_context("   ") == ""

    def test_loads_source_context_file(self, tmp_path):
        """Test loading a configured source context file."""
        context_file = tmp_path / "source_context.md"
        context_file.write_text("Audience asks for implementation proof.", encoding="utf-8")

        assert load_optional_source_context(str(context_file)) == "Audience asks for implementation proof."

    def test_missing_source_context_file_raises_clear_error(self, tmp_path):
        """Test configured but missing source context path fails clearly."""
        missing_file = tmp_path / "missing.md"

        with pytest.raises(FileNotFoundError, match="Source context file not found"):
            load_optional_source_context(str(missing_file))

    def test_source_context_is_truncated(self, tmp_path):
        """Test large source context files are bounded before prompt use."""
        context_file = tmp_path / "source_context.md"
        context_file.write_text("A" * (MAX_SOURCE_CONTEXT_CHARS + 100), encoding="utf-8")

        assert len(load_optional_source_context(str(context_file))) == MAX_SOURCE_CONTEXT_CHARS
