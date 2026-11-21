# Testing Guide

## Overview

The Tweet Processor has a comprehensive offline test suite with **212 tests** achieving **100% pass rate** with **0 warnings**.

| Metric | Value |
|--------|-------|
| **Total Tests** | 212 |
| **Pass Rate** | 100% |
| **Warnings** | 0 |
| **Runtime** | ~35 seconds |

---

## Quick Start

```bash
# Run all tests
python -m pytest tests/ -v

# Run with summary output
python -m pytest tests/ -v --tb=line -q
```

---

## Test Files

| File | Tests | Description |
|------|-------|-------------|
| `test_article_parser.py` | 23 | Article parsing, markdown extraction, edge cases |
| `test_url_validator.py` | 26 | URL format validation, uniqueness, article validation |
| `test_url_integrity.py` | 7 | URL mappings, consistency across workflow |
| `test_tweet_composer.py` | 48 | Tweet composition, hashtags, character limits, shorten retry, timeout retry |
| `test_workflow_state.py` | 8 | State loading/saving, article progression |
| `test_edge_cases.py` | 22 | Error handling, unicode, concurrent operations |
| `test_integration_workflow.py` | 5 | End-to-end workflow execution |
| `test_workflow_integration.py` | 17 | Full workflow URL integrity; composes only up to the current variation |
| `test_claude_llm.py` | 13 | Claude wrapper: thinking/effort per model, refusal/truncation errors, cost estimate, usage log |
| `test_twitter_post_retry.py` | 9 | Posting retries only for connection failures before the request is sent |
| `test_tee_run.py` | 7 | Live output streaming, exit codes, log integrity |
| `test_content_hash_cache.py` | 27 | Analysis cache content hash: normalization, legacy adoption, re-analysis on edits, weekly and pipeline paths |

---

## Test Markers

Run tests by category using pytest markers:

```bash
# Unit tests
python -m pytest tests/ -v -m "unit"

# Integration tests
python -m pytest tests/ -v -m "integration"

# URL validation tests
python -m pytest tests/ -v -m "url_validation"

# Edge case tests
python -m pytest tests/ -v -m "edge_case"

# Slow tests
python -m pytest tests/ -v -m "slow"
```

---

## Running Specific Tests

```bash
# Run a specific test file
python -m pytest tests/test_article_parser.py -v

# Run a specific test function
python -m pytest tests/test_article_parser.py::TestArticle::test_article_creation -v

# Run tests matching a pattern
python -m pytest tests/ -v -k "url"
```

---

## Test Coverage

```bash
# Run with coverage report
python -m pytest tests/ --cov=src --cov-report=html

# Terminal coverage summary
python -m pytest tests/ --cov=src --cov-report=term
```

---

## Key Test Fixtures

Located in `tests/conftest.py`:

| Fixture | Purpose |
|---------|---------|
| `_isolate_from_live_services` (autouse) | Blocks live Anthropic calls; points `TOKEN_USAGE_LOG`, `TWEET_AUDIT_LOG` and `WORKFLOW_STATE_FILE` at the test's temp dir |
| `sample_workflow_state` | Sample workflow state with 5 articles |
| `isolated_workflow_state_file` | Temporary workflow state for isolated testing |
| `temp_articles_file` | Temporary articles markdown file |
| `mock_mcp_app` | Mocked MCP application |
| `mock_tweet_composer` | Mocked tweet composer agent |
| `mock_content_analyzer` | Mocked content analyzer agent |
| `expected_url_mappings` | URL-to-article mapping expectations |
| `sample_article_insights` | Sample article analysis data |
| `sample_tweet_variations` | Sample tweet variations |
| `corrupted_markdown_content` | Malformed data for error testing |
| `invalid_articles_data` | Invalid article data for error handling |

---

## Test Categories

### Unit Tests
Test individual components in isolation:
- Article dataclass properties
- Parser initialization and methods
- URL format validation
- Tweet composition logic
- Hashtag selection
- Character counting

### Integration Tests
Test component interactions:
- End-to-end workflow execution
- Article reading and parsing
- URL integrity through workflow
- State management

### Edge Case Tests
Test error handling and boundary conditions:
- Empty files and missing data
- Very long titles and URLs
- Special characters and unicode
- Concurrent operations
- Zero/negative values

---

## Configuration

Test configuration is in `pytest.ini`:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
markers =
    unit: Unit tests
    integration: Integration tests
    url_validation: URL validation tests
    edge_case: Edge case and error handling tests
    slow: Slow running tests
```

---

## Troubleshooting

### Common Issues

**Marker warnings**: Ensure `pytest.ini` uses `[pytest]` header (not `[tool:pytest]`)

**Import errors**: Verify `src` is in Python path (handled by `conftest.py`)

**Slow tests**: Use `-m "not slow"` to skip slow tests during development

---

*Last updated: November 20, 2026 (counts verified against a full 212-test run)*

