"""
Unit Tests for Tweet Composer Agent
Tests character limits, hashtag generation, insight selection, and content formatting.
"""

import pytest
import os
import sys
from unittest.mock import Mock, AsyncMock, patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.mcp_tweet_composer_agent import MCPTweetComposerAgent, Tweet


@pytest.mark.unit
class TestTweetDataclass:
    """Test suite for Tweet dataclass."""

    def test_tweet_creation(self):
        """Test creating a Tweet instance."""
        tweet = Tweet(
            article_number=1,
            variation_number=1,
            content="Test tweet content",
            character_count=150,
            hashtags=["#AI", "#DataStrategy"],
            insights_used=["Test insight"],
            focus_theme="strategic_value"
        )

        assert tweet.article_number == 1
        assert tweet.variation_number == 1
        assert tweet.content == "Test tweet content"
        assert tweet.character_count == 150
        assert tweet.hashtags == ["#AI", "#DataStrategy"]
        assert tweet.insights_used == ["Test insight"]
        assert tweet.focus_theme == "strategic_value"


@pytest.mark.unit
class TestTweetComposerInitialization:
    """Test suite for MCPTweetComposerAgent initialization."""

    def test_composer_creation_without_agent(self):
        """Test creating composer without pre-configured agent."""
        composer = MCPTweetComposerAgent()
        assert composer.agent is not None
        assert composer.llm is None

    def test_composer_creation_with_agent(self):
        """Test creating composer with pre-configured agent."""
        mock_agent = Mock()
        composer = MCPTweetComposerAgent(agent=mock_agent)
        assert composer.agent == mock_agent


@pytest.mark.unit
class TestHashtagSelection:
    """Test suite for hashtag selection logic."""

    def test_select_hashtags_default(self):
        """Test default hashtag selection."""
        composer = MCPTweetComposerAgent()
        hashtags = composer._select_hashtags(["General", "Business"])

        assert "#AI" in hashtags
        assert len(hashtags) == 2

    def test_select_hashtags_machine_learning(self):
        """Test hashtag selection for machine learning themes."""
        composer = MCPTweetComposerAgent()
        hashtags = composer._select_hashtags(["Machine Learning", "AI"])

        assert "#AI" in hashtags
        assert "#MachineLearning" in hashtags

    def test_select_hashtags_leadership(self):
        """Test hashtag selection for leadership themes."""
        composer = MCPTweetComposerAgent()
        hashtags = composer._select_hashtags(["Leadership", "Management"])

        assert "#AI" in hashtags
        assert "#Leadership" in hashtags

    def test_select_hashtags_data_analytics(self):
        """Test hashtag selection for data analytics themes."""
        composer = MCPTweetComposerAgent()
        hashtags = composer._select_hashtags(["Data Analytics", "Business Intelligence"])

        assert "#AI" in hashtags
        assert "#DataAnalytics" in hashtags or "#DataStrategy" in hashtags

    def test_select_hashtags_transformation(self):
        """Test hashtag selection for transformation themes."""
        composer = MCPTweetComposerAgent()
        hashtags = composer._select_hashtags(["Digital Transformation", "Innovation"])

        assert "#AI" in hashtags
        assert "#DigitalTransformation" in hashtags or "#DataStrategy" in hashtags

    def test_select_hashtags_always_includes_ai(self):
        """Test that #AI is always included."""
        composer = MCPTweetComposerAgent()

        # Test with various themes
        for themes in [["Business"], ["Strategy"], ["Technology"], []]:
            hashtags = composer._select_hashtags(themes)
            assert "#AI" in hashtags

    def test_select_hashtags_max_two_hashtags(self):
        """Test that maximum 2 hashtags are returned."""
        composer = MCPTweetComposerAgent()
        hashtags = composer._select_hashtags(["Machine Learning", "Leadership", "Data", "Transform"])

        assert len(hashtags) == 2


@pytest.mark.unit
@pytest.mark.asyncio
class TestTweetComposition:
    """Test suite for tweet composition functionality."""

    async def test_compose_tweet_basic(self, sample_article_insights):
        """Test basic tweet composition."""
        composer = MCPTweetComposerAgent()

        # Mock the LLM
        mock_llm = AsyncMock()
        mock_llm.generate_str = AsyncMock(return_value="AI success depends on organizational readiness 🚀")
        composer.llm = mock_llm

        tweet_content, insights_used = await composer.compose_tweet(
            article_title=sample_article_insights["article_title"],
            article_url=sample_article_insights["article_url"],
            insights=sample_article_insights["key_insights"],
            themes=sample_article_insights["themes"],
            variation_number=1
        )

        assert tweet_content is not None
        assert len(insights_used) > 0
        assert sample_article_insights["article_url"] in tweet_content
        assert "#AI" in tweet_content

    async def test_compose_tweet_character_limit(self, sample_article_insights):
        """Test that composed tweets respect character limits."""
        composer = MCPTweetComposerAgent()

        # Mock LLM with very long content
        mock_llm = AsyncMock()
        long_content = "A" * 300  # Exceeds available space
        mock_llm.generate_str = AsyncMock(return_value=long_content)
        composer.llm = mock_llm

        tweet_content, _ = await composer.compose_tweet(
            article_title=sample_article_insights["article_title"],
            article_url=sample_article_insights["article_url"],
            insights=sample_article_insights["key_insights"],
            themes=sample_article_insights["themes"],
            variation_number=1
        )

        # Calculate effective character count (URL is shortened to 23 chars)
        parts = tweet_content.split('\n\n')
        main_content = parts[0]
        hashtags = ' '.join([word for word in tweet_content.split() if word.startswith('#')])
        effective_count = len(main_content) + 23 + len(hashtags) + 4

        # Should be truncated to fit within 280 characters
        assert effective_count <= 280

    async def test_compose_tweet_includes_url(self, sample_article_insights):
        """Test that composed tweet includes the article URL."""
        composer = MCPTweetComposerAgent()

        mock_llm = AsyncMock()
        mock_llm.generate_str = AsyncMock(return_value="Test tweet content")
        composer.llm = mock_llm

        tweet_content, _ = await composer.compose_tweet(
            article_title=sample_article_insights["article_title"],
            article_url=sample_article_insights["article_url"],
            insights=sample_article_insights["key_insights"],
            themes=sample_article_insights["themes"],
            variation_number=1
        )

        assert sample_article_insights["article_url"] in tweet_content

    async def test_compose_tweet_includes_hashtags(self, sample_article_insights):
        """Test that composed tweet includes hashtags."""
        composer = MCPTweetComposerAgent()

        mock_llm = AsyncMock()
        mock_llm.generate_str = AsyncMock(return_value="Test tweet content")
        composer.llm = mock_llm

        tweet_content, _ = await composer.compose_tweet(
            article_title=sample_article_insights["article_title"],
            article_url=sample_article_insights["article_url"],
            insights=sample_article_insights["key_insights"],
            themes=sample_article_insights["themes"],
            variation_number=1
        )

        assert "#AI" in tweet_content
        hashtags = [word for word in tweet_content.split() if word.startswith('#')]
        assert len(hashtags) >= 1


@pytest.mark.unit
@pytest.mark.asyncio
class TestMultipleVariations:
    """Test suite for composing multiple tweet variations."""

    async def test_compose_multiple_variations_count(self, sample_article_insights):
        """Test composing multiple variations returns correct count."""
        composer = MCPTweetComposerAgent()

        mock_llm = AsyncMock()
        mock_llm.generate_str = AsyncMock(return_value="Test tweet content")
        composer.llm = mock_llm

        tweets = await composer.compose_multiple_variations(
            article_number=1,
            article_title=sample_article_insights["article_title"],
            article_url=sample_article_insights["article_url"],
            insights=sample_article_insights["key_insights"],
            themes=sample_article_insights["themes"],
            num_variations=4
        )

        assert len(tweets) == 4
        assert all(isinstance(t, Tweet) for t in tweets)

    async def test_compose_multiple_variations_character_limits(self, sample_article_insights):
        """Test that all variations respect character limits."""
        composer = MCPTweetComposerAgent()

        mock_llm = AsyncMock()
        mock_llm.generate_str = AsyncMock(return_value="Test tweet content for character limit testing")
        composer.llm = mock_llm

        tweets = await composer.compose_multiple_variations(
            article_number=1,
            article_title=sample_article_insights["article_title"],
            article_url=sample_article_insights["article_url"],
            insights=sample_article_insights["key_insights"],
            themes=sample_article_insights["themes"],
            num_variations=4
        )

        for tweet in tweets:
            assert tweet.character_count <= 280




@pytest.mark.unit
class TestGroundingValidation:
    """Tests for the _check_grounding deterministic validator."""

    def test_passes_clean_paraphrase(self):
        """A tweet that only rephrases the insight produces no violations."""
        composer = MCPTweetComposerAgent()
        insight = "Strategic fit between AI approach and business problem drives success"
        tweet = "Strategic fit drives AI success 💡 Match approach to business problem"
        violations = composer._check_grounding(insight, tweet)
        assert violations == []

    def test_flags_statistic_not_in_insight(self):
        """A numeric claim in the tweet that is absent from the insight is flagged."""
        composer = MCPTweetComposerAgent()
        insight = "Organizational readiness matters more than technical sophistication"
        tweet = "80% of AI failures trace back to org issues, not technology 🚀"
        violations = composer._check_grounding(insight, tweet)
        assert any("80" in v for v in violations), (
            f"Expected a violation for '80' (not in insight), got: {violations}"
        )

    def test_flags_proper_noun_not_in_insight(self):
        """A multi-word proper noun in the tweet absent from the insight is flagged."""
        composer = MCPTweetComposerAgent()
        insight = "Data quality is the foundation of reliable AI outputs"
        tweet = "McKinsey Research confirms data quality drives AI reliability 📊"
        violations = composer._check_grounding(insight, tweet)
        assert any("McKinsey" in v for v in violations), (
            f"Expected a violation for 'McKinsey Research', got: {violations}"
        )

    def test_passes_number_present_in_insight(self):
        """A number that IS in the insight is not flagged."""
        composer = MCPTweetComposerAgent()
        insight = "Companies investing in 3 core data pillars see measurable AI ROI"
        tweet = "3 data pillars determine AI ROI 📊 Invest in the right foundations"
        violations = composer._check_grounding(insight, tweet)
        number_violations = [v for v in violations if "'3'" in v]
        assert number_violations == [], (
            f"'3' is present in the insight and should not be flagged, got: {violations}"
        )

    def test_passes_proper_noun_present_in_insight(self):
        """A proper-noun phrase that IS in the insight is not flagged."""
        composer = MCPTweetComposerAgent()
        insight = "Cornell University's program emphasises a business-first framing of AI"
        tweet = "Cornell University proves business-first AI beats tech-first thinking 🎓"
        violations = composer._check_grounding(insight, tweet)
        noun_violations = [v for v in violations if "Cornell University" in v]
        assert noun_violations == [], (
            f"'Cornell University' is in the insight and should not be flagged, got: {violations}"
        )

    def test_flags_multiple_violations(self):
        """Multiple ungrounded claims in a single tweet are all reported."""
        composer = MCPTweetComposerAgent()
        insight = "AI adoption requires cultural change inside the organisation"
        tweet = "Harvard Business School says 75% of AI projects fail without culture change 📊"
        violations = composer._check_grounding(insight, tweet)
        assert len(violations) >= 2, (
            f"Expected at least 2 violations (stat + proper noun), got: {violations}"
        )

    def test_returns_list_type(self):
        """_check_grounding always returns a list regardless of input."""
        composer = MCPTweetComposerAgent()
        result = composer._check_grounding("some insight", "some tweet content")
        assert isinstance(result, list)
