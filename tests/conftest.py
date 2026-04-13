"""
Pytest configuration and fixtures for Tweet Processor tests.
"""

import pytest
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, List, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture
def sample_workflow_state():
    """Sample workflow state data for testing."""
    return {
        "current_article": 3,
        "current_variation": 4,
        "last_posted": "2025-10-10T15:30:00.000000",
        "total_posts": 11,
        "articles_cache": [
            {
                "number": 1,
                "title": "Creating Business Value with AI (Part 2) - What I Learned from Cornell (Republished Version)",
                "url": "https://www.linkedin.com/pulse/creating-business-value-ai-part-1-what-i-learned-from-lim-ywfmc/",
                "content": "Sample content...",
                "word_count": 191,
                "has_title": True,
                "has_url": True
            },
            {
                "number": 2,
                "title": "Leveraging Data for AI Solutions (Part 3) - Data Quality and Preparation",
                "url": "https://www.linkedin.com/pulse/leveraging-data-ai-solutions-part-3-aaron-lim/",
                "content": "Sample content...",
                "word_count": 112,
                "has_title": True,
                "has_url": True
            },
            {
                "number": 3,
                "title": "AI Implementation Strategies for Business Leaders",
                "url": "https://www.linkedin.com/pulse/ai-implementation-strategies-business-leaders-aaron-lim/",
                "content": "Sample content...",
                "word_count": 97,
                "has_title": True,
                "has_url": True
            },
            {
                "number": 4,
                "title": "Ethical AI and Responsible Innovation",
                "url": "https://www.linkedin.com/pulse/ethical-ai-responsible-innovation-aaron-lim/",
                "content": "Sample content...",
                "word_count": 85,
                "has_title": True,
                "has_url": True
            },
            {
                "number": 5,
                "title": "Measuring AI Success - Metrics and KPIs",
                "url": "https://www.linkedin.com/pulse/measuring-ai-success-metrics-kpis-aaron-lim/",
                "content": "Sample content...",
                "word_count": 78,
                "has_title": True,
                "has_url": True
            }
        ],
        "analysis_1": {
            "article_number": 1,
            "article_title": "Creating Business Value with AI (Part 2) - What I Learned from Cornell (Republished Version)",
            "article_url": "https://www.linkedin.com/pulse/creating-business-value-ai-part-1-what-i-learned-from-lim-ywfmc/",
            "key_insights": ["Insight 1", "Insight 2"],
            "themes": ["AI", "Business"]
        },
        "analysis_2": {
            "article_number": 2,
            "article_title": "Leveraging Data for AI Solutions (Part 3) - Data Quality and Preparation",
            "article_url": "https://www.linkedin.com/pulse/leveraging-data-ai-solutions-part-3-aaron-lim/",
            "key_insights": ["Insight 1", "Insight 2"],
            "themes": ["Data", "AI"]
        },
        "analysis_3": {
            "article_number": 3,
            "article_title": "AI Implementation Strategies for Business Leaders",
            "article_url": "https://www.linkedin.com/pulse/ai-implementation-strategies-business-leaders-aaron-lim/",
            "key_insights": ["Insight 1", "Insight 2"],
            "themes": ["AI", "Strategy"]
        },
        "analysis_4": {
            "article_number": 4,
            "article_title": "Ethical AI and Responsible Innovation",
            "article_url": "https://www.linkedin.com/pulse/ethical-ai-responsible-innovation-aaron-lim/",
            "key_insights": ["Insight 1", "Insight 2"],
            "themes": ["Ethics", "AI"]
        },
        "analysis_5": {
            "article_number": 5,
            "article_title": "Measuring AI Success - Metrics and KPIs",
            "article_url": "https://www.linkedin.com/pulse/measuring-ai-success-metrics-kpis-aaron-lim/",
            "key_insights": ["Insight 1", "Insight 2"],
            "themes": ["Metrics", "AI"]
        }
    }


@pytest.fixture
def isolated_workflow_state_file(tmp_path, sample_workflow_state):
    """
    Create isolated workflow state file for testing.

    This fixture creates a temporary workflow_state.json file with controlled test data
    to prevent integration tests from using the real workflow state file.
    """
    import json
    state_file = tmp_path / "workflow_state.json"
    with open(state_file, 'w', encoding='utf-8') as f:
        json.dump(sample_workflow_state, f, indent=2)
    return state_file


@pytest.fixture
def isolated_workflow_state_data(sample_workflow_state):
    """
    Provide isolated workflow state data for testing.

    Returns a copy of sample_workflow_state to prevent test pollution.
    """
    import copy
    return copy.deepcopy(sample_workflow_state)


@pytest.fixture
def mock_mcp_app():
    """Mock MCP App for testing."""
    mock_app = Mock()
    mock_app.name = "test_tweet_processor"
    return mock_app


@pytest.fixture
def mock_tweet_composer():
    """Mock tweet composer agent."""
    mock_composer = Mock()
    mock_composer.compose_tweet = AsyncMock()
    mock_composer.compose_multiple_variations = AsyncMock()
    return mock_composer


@pytest.fixture
def mock_content_analyzer():
    """Mock content analyzer agent."""
    mock_analyzer = Mock()
    mock_analyzer.analyze_article = AsyncMock()
    return mock_analyzer


@pytest.fixture
def expected_url_mappings():
    """Expected URL mappings for validation."""
    return {
        1: "https://www.linkedin.com/pulse/creating-business-value-ai-part-1-what-i-learned-from-lim-ywfmc/",
        2: "https://www.linkedin.com/pulse/leveraging-data-ai-solutions-part-3-aaron-lim/",
        3: "https://www.linkedin.com/pulse/ai-implementation-strategies-business-leaders-aaron-lim/",
        4: "https://www.linkedin.com/pulse/ethical-ai-responsible-innovation-aaron-lim/",
        5: "https://www.linkedin.com/pulse/measuring-ai-success-metrics-kpis-aaron-lim/"
    }


@pytest.fixture
def invalid_articles_data():
    """Invalid article data for testing error handling."""
    return [
        {
            "number": 1,
            "title": "Test Article 1",
            "url": "",  # Empty URL
            "content": "Test content"
        },
        {
            "number": 2,
            "title": "Test Article 2",
            "url": "https://www.linkedin.com/pulse/leveraging-data-ai-solutions-part-3-aaron-lim/",  # Wrong URL for article 2
            "content": "Test content"
        }
    ]


@pytest.fixture
def sample_article_insights():
    """Sample article insights for testing."""
    return {
        "article_number": 1,
        "article_title": "Creating Business Value with AI",
        "article_url": "https://www.linkedin.com/pulse/creating-business-value-ai-part-1-what-i-learned-from-lim-ywfmc/",
        "key_insights": [
            "AI success depends on organizational readiness more than technology",
            "Strategic fit beats technical sophistication in AI implementations",
            "Data quality compounds over time and delivers exponential ROI",
            "User adoption is the ultimate measure of AI value",
            "Start with business problems, not AI solutions",
            "Measure AI success through process efficiency gains",
            "Cultural alignment drives sustainable AI transformation"
        ],
        "themes": ["AI", "Business Strategy", "Data Quality"],
        "expert_references": ["Andrew Ng", "Cassie Kozyrkov"],
        "frameworks_mentioned": ["CRISP-DM", "Agile AI"]
    }


@pytest.fixture
def sample_tweet_variations():
    """Sample tweet variations for testing."""
    return [
        {
            "article_number": 1,
            "variation_number": 1,
            "content": "AI success = 80% org readiness, 20% tech 🚀\n\nhttps://www.linkedin.com/pulse/creating-business-value-ai-part-1-what-i-learned-from-lim-ywfmc/\n\n#AI #DataStrategy",
            "character_count": 150,
            "hashtags": ["#AI", "#DataStrategy"],
            "insights_used": ["AI success depends on organizational readiness more than technology"],
            "focus_theme": "strategic_value"
        },
        {
            "article_number": 1,
            "variation_number": 2,
            "content": "Strategic fit beats technical sophistication 💡\n\nhttps://www.linkedin.com/pulse/creating-business-value-ai-part-1-what-i-learned-from-lim-ywfmc/\n\n#AI #DataStrategy",
            "character_count": 145,
            "hashtags": ["#AI", "#DataStrategy"],
            "insights_used": ["Strategic fit beats technical sophistication in AI implementations"],
            "focus_theme": "systematic_approach"
        }
    ]


@pytest.fixture
def corrupted_markdown_content():
    """Corrupted Markdown content for testing error handling."""
    return """# Newsletter Articles

## Article #1

**Title:** Missing URL Article

**Content:**

This article is missing the URL field.

**Metadata:**
- Word Count: 50
- Status: Active

---

## Article #2

**URL:** https://www.linkedin.com/pulse/test-article-aaron-lim/

This article is missing the Title field and has malformed structure.

---

## Article #3

**Title:** Incomplete Article

**URL:** https://www.linkedin.com/pulse/incomplete-aaron-lim/

**Content:**

This article is missing the Metadata section.
"""


@pytest.fixture
def temp_articles_file(tmp_path):
    """Fixture providing a temporary articles file with sample data for testing."""
    content = """# LinkedIn Articles Collection

## Article #1

**Title:** Creating Business Value with AI (Part 1)

**URL:** https://www.linkedin.com/pulse/creating-business-value-ai-part-1-what-i-learned-from-lim-ywfmc/

**Content:**

AI business value creation requires strategic thinking and careful implementation.

**Metadata:**
- Word Count: 150
- Status: Active

---

## Article #2

**Title:** Data Strategy for AI Success

**URL:** https://www.linkedin.com/pulse/data-strategy-ai-success-aaron-lim/

**Content:**

Effective data quality is essential for AI success.

**Metadata:**
- Word Count: 200
- Status: Active

---

## Article #3

**Title:** AI Implementation Best Practices

**URL:** https://www.linkedin.com/pulse/ai-implementation-best-practices-aaron-lim/

**Content:**

This article provides practical guidance for AI implementation.

**Metadata:**
- Word Count: 175
- Status: Active

---
"""

    file_path = tmp_path / "articles.md"
    file_path.write_text(content, encoding='utf-8')
    return file_path


@pytest.fixture(autouse=True)
def setup_logging():
    """Setup logging for tests."""
    import logging
    logging.basicConfig(level=logging.INFO)
    yield
    # Cleanup after test
    logging.getLogger().handlers.clear()
