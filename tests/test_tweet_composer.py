"""
Unit Tests for Tweet Composer Agent
Tests character limits, hashtag generation, insight selection, and content formatting.
"""

import pytest
import os
import re
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


@pytest.mark.unit
class TestTweetContentSanitization:
    """
    Tests for _sanitize_tweet_content.

    Regression suite for the 2026-07-06 incident where the LLM appended a
    character-count annotation to the tweet text and it was posted verbatim.
    """

    CLEAN_TWEET = "Data quality compounds over time 📊 Clean data delivers 10x ROI"

    def test_clean_tweet_unchanged(self):
        """A well-formed response passes through untouched."""
        result = MCPTweetComposerAgent._sanitize_tweet_content(self.CLEAN_TWEET)
        assert result == self.CLEAN_TWEET

    def test_strips_trailing_inline_char_count(self):
        """Regression: '(147 characters)' appended on the tweet line is removed."""
        raw = f"{self.CLEAN_TWEET} (147 characters)"
        result = MCPTweetComposerAgent._sanitize_tweet_content(raw)
        assert result == self.CLEAN_TWEET

    def test_strips_trailing_char_count_line(self):
        """Regression: a standalone 'Character count: 147' line is removed."""
        raw = f"{self.CLEAN_TWEET}\nCharacter count: 147"
        result = MCPTweetComposerAgent._sanitize_tweet_content(raw)
        assert result == self.CLEAN_TWEET

    def test_strips_ratio_annotation_line(self):
        """A trailing '147/280' or '(147/280 chars)' line is removed."""
        for meta in ["147/280", "(147/280)", "[147/280 chars]", "147/280 characters"]:
            raw = f"{self.CLEAN_TWEET}\n{meta}"
            result = MCPTweetComposerAgent._sanitize_tweet_content(raw)
            assert result == self.CLEAN_TWEET, f"Failed to strip: {meta!r}"

    def test_strips_multiple_meta_lines(self):
        """Several trailing meta lines are all removed."""
        raw = f"{self.CLEAN_TWEET}\n(147 chars)\nCharacter count: 147/280"
        result = MCPTweetComposerAgent._sanitize_tweet_content(raw)
        assert result == self.CLEAN_TWEET

    def test_strips_code_fences(self):
        """A tweet wrapped in Markdown code fences is unwrapped."""
        raw = f"```\n{self.CLEAN_TWEET}\n```"
        result = MCPTweetComposerAgent._sanitize_tweet_content(raw)
        assert result == self.CLEAN_TWEET

    def test_strips_code_fences_with_language_tag(self):
        """A ```text fence with a language tag is unwrapped."""
        raw = f"```text\n{self.CLEAN_TWEET}\n```"
        result = MCPTweetComposerAgent._sanitize_tweet_content(raw)
        assert result == self.CLEAN_TWEET

    def test_strips_surrounding_quotes(self):
        """Straight and curly quotes wrapping the tweet are removed."""
        for raw in [f'"{self.CLEAN_TWEET}"', f"“{self.CLEAN_TWEET}”"]:
            result = MCPTweetComposerAgent._sanitize_tweet_content(raw)
            assert result == self.CLEAN_TWEET, f"Failed to unquote: {raw!r}"

    def test_strips_leading_tweet_label(self):
        """A leading 'Tweet:' or 'Here is your tweet:' label is removed."""
        for label in ["Tweet: ", "Your tweet: ", "Here is your tweet: ", "Here's the tweet: "]:
            raw = f"{label}{self.CLEAN_TWEET}"
            result = MCPTweetComposerAgent._sanitize_tweet_content(raw)
            assert result == self.CLEAN_TWEET, f"Failed to strip label: {label!r}"

    def test_strips_combined_meta(self):
        """Fences, label, quotes, and count annotation together are all removed."""
        raw = f'```\nTweet: "{self.CLEAN_TWEET}"\n(147 characters)\n```'
        result = MCPTweetComposerAgent._sanitize_tweet_content(raw)
        assert result == self.CLEAN_TWEET

    def test_preserves_legitimate_numbers(self):
        """Numbers that are tweet content ('10x ROI', '80%') are not stripped."""
        tweet = "AI success = 80% org readiness, 20% tech 🚀 Culture drives 10x results"
        result = MCPTweetComposerAgent._sanitize_tweet_content(tweet)
        assert result == tweet

    def test_preserves_trailing_bare_number_line(self):
        """A bare number line without a 'chars' word or ratio is NOT treated as meta."""
        tweet = "Three pillars of AI readiness; Rank yours from 1 to\n3"
        result = MCPTweetComposerAgent._sanitize_tweet_content(tweet)
        assert result == tweet

    def test_preserves_internal_parenthetical(self):
        """A parenthetical that is not a count annotation survives."""
        tweet = "Good Old Fashioned AI (GOFAI) still powers rules engines 💡"
        result = MCPTweetComposerAgent._sanitize_tweet_content(tweet)
        assert result == tweet


@pytest.mark.unit
@pytest.mark.asyncio
class TestComposeTweetSanitization:
    """End-to-end regression: compose_tweet must sanitize the LLM response."""

    async def test_char_count_annotation_never_reaches_tweet(self, sample_article_insights):
        """Regression for 2026-07-06: an appended count never reaches the final tweet."""
        composer = MCPTweetComposerAgent()

        mock_llm = AsyncMock()
        mock_llm.generate_str = AsyncMock(
            return_value="Strategic fit beats technical sophistication 💡 (63 characters)"
        )
        composer.llm = mock_llm

        tweet_content, _ = await composer.compose_tweet(
            article_title=sample_article_insights["article_title"],
            article_url=sample_article_insights["article_url"],
            insights=sample_article_insights["key_insights"],
            themes=sample_article_insights["themes"],
            variation_number=1
        )

        assert "characters" not in tweet_content
        assert "63" not in tweet_content
        assert tweet_content.startswith("Strategic fit beats technical sophistication 💡")

    async def test_meta_line_never_reaches_tweet(self, sample_article_insights):
        """A standalone 'Character count' line never reaches the final tweet."""
        composer = MCPTweetComposerAgent()

        mock_llm = AsyncMock()
        mock_llm.generate_str = AsyncMock(
            return_value="Data quality drives AI ROI 📊\n\nCharacter count: 29/280"
        )
        composer.llm = mock_llm

        tweet_content, _ = await composer.compose_tweet(
            article_title=sample_article_insights["article_title"],
            article_url=sample_article_insights["article_url"],
            insights=sample_article_insights["key_insights"],
            themes=sample_article_insights["themes"],
            variation_number=1
        )

        assert "Character count" not in tweet_content
        assert "29/280" not in tweet_content
        assert "Data quality drives AI ROI 📊" in tweet_content


@pytest.mark.unit
@pytest.mark.asyncio
class TestShortenRetry:
    """Over-length tweets get one shorten-rewrite retry before truncation is applied."""

    LONG = "Strategic alignment beats technical sophistication in every AI program " * 5  # ~360 chars
    SHORT = "Strategic alignment beats technical sophistication in AI programs 🎯"

    async def _compose(self, composer, sample_article_insights):
        tweet_content, _ = await composer.compose_tweet(
            article_title=sample_article_insights["article_title"],
            article_url=sample_article_insights["article_url"],
            insights=sample_article_insights["key_insights"],
            themes=sample_article_insights["themes"],
            variation_number=1
        )
        return tweet_content.split('\n\n')[0]

    async def test_short_tweet_makes_one_call(self, sample_article_insights):
        composer = MCPTweetComposerAgent()
        composer.llm = AsyncMock()
        composer.llm.generate_str = AsyncMock(return_value=self.SHORT)

        main = await self._compose(composer, sample_article_insights)

        assert main == self.SHORT
        assert composer.llm.generate_str.await_count == 1

    async def test_retry_rewrite_replaces_long_tweet(self, sample_article_insights):
        composer = MCPTweetComposerAgent()
        composer.llm = AsyncMock()
        composer.llm.generate_str = AsyncMock(side_effect=[self.LONG, self.SHORT])

        main = await self._compose(composer, sample_article_insights)

        assert main == self.SHORT
        assert not main.endswith('…')
        assert composer.llm.generate_str.await_count == 2
        retry_prompt = composer.llm.generate_str.await_args_list[1].kwargs["message"]
        assert self.LONG.strip() in retry_prompt

    async def test_retry_prompt_aims_below_limit(self, sample_article_insights):
        composer = MCPTweetComposerAgent()
        composer.llm = AsyncMock()
        composer.llm.generate_str = AsyncMock(side_effect=[self.LONG, self.SHORT])

        await self._compose(composer, sample_article_insights)

        retry_prompt = composer.llm.generate_str.await_args_list[1].kwargs["message"]
        limit = int(re.search(r"The limit is (\d+) characters", retry_prompt).group(1))
        assert f"aim for about {limit - MCPTweetComposerAgent.SHORTEN_TARGET_MARGIN})" in retry_prompt
        assert MCPTweetComposerAgent.SHORTEN_TARGET_MARGIN == 30

    async def test_still_long_after_retry_is_truncated(self, sample_article_insights):
        composer = MCPTweetComposerAgent()
        composer.llm = AsyncMock()
        composer.llm.generate_str = AsyncMock(side_effect=[self.LONG, self.LONG[:-40]])

        main = await self._compose(composer, sample_article_insights)

        assert main.endswith('…')
        assert composer.llm.generate_str.await_count == 2

    async def test_failed_retry_falls_back_to_truncation(self, sample_article_insights):
        composer = MCPTweetComposerAgent()
        composer.llm = AsyncMock()
        composer.llm.generate_str = AsyncMock(side_effect=[self.LONG, RuntimeError("API error")])

        main = await self._compose(composer, sample_article_insights)

        assert main.endswith('…')

    async def test_retry_target_stays_positive_for_small_limits(self):
        composer = MCPTweetComposerAgent()
        composer.llm = AsyncMock()
        composer.llm.generate_str = AsyncMock(return_value="Short")

        await composer._shorten_tweet("x" * 40, max_chars=20)
        assert "aim for about 10)" in composer.llm.generate_str.await_args.kwargs["message"]

        await composer._shorten_tweet("x" * 40, max_chars=1)
        assert "aim for about 1)" in composer.llm.generate_str.await_args.kwargs["message"]
