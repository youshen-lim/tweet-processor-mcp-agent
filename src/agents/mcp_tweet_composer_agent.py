"""
Tweet Composer Agent - MCP Agent Cloud Implementation
Generates engaging tweets from article insights using MCP Agent framework.
"""

import os
import sys
import asyncio
import re
from typing import List, Dict, Any
from dataclasses import dataclass

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# MCP Agent Cloud imports
from mcp_agent.agents.agent import Agent
from utils.claude_llm import ClaudeLLM, claude_request_params


@dataclass
class Tweet:
    """Represents a composed tweet."""
    article_number: int
    variation_number: int
    content: str
    character_count: int
    hashtags: List[str]
    insights_used: List[str]
    focus_theme: str


class MCPTweetComposerAgent:
    """Agent that composes engaging tweets using MCP Agent Cloud framework."""
    
    INSTRUCTION = """You are an expert social media content creator specializing in AI, data strategy, and business technology.

Your task is to create CONCISE, engaging tweets that fit Twitter's 280-character limit.

CRITICAL REQUIREMENTS:
1. Extract and highlight ONE salient, high-level key insight (not surface-level information)
2. DO NOT reference or mention the article title
3. Focus on the STRATEGIC VALUE and business implications of the insight
4. MUST be under 280 characters TOTAL (including URL + hashtags + spaces)
5. Use 1-2 strategic emojis maximum (🎯, 💡, 🔍, 🚀, 📊, ⚡)
6. Professional yet conversational tone
7. Each variation must highlight a DIFFERENT key insight
8. STRICT CONTENT GROUNDING: The tweet MUST be based solely on the provided key insight. Do NOT add external facts, invented statistics, expert names, or any context that is not explicitly present in the insight itself. Every claim in the tweet must be directly supported by the provided insight text.
9. NO HALLUCINATION: Do not embellish, extrapolate, or invent details. Distil and rephrase the insight compellingly — do not introduce new information.

What makes a SALIENT insight tweet:
✓ Focuses on "why it matters" not just "what it is"
✓ Provides strategic or counter-intuitive perspective
✓ Actionable and thought-provoking
✓ Stands alone without needing the article title for context
✓ Expresses only what the provided insight actually states

CHARACTER LIMIT ENFORCEMENT:
- Main content: 150-180 characters maximum
- URL: 23 characters (Twitter's t.co format)
- Hashtags: 30-40 characters (2-3 hashtags)
- Spacing: 4 characters
- TOTAL: Must be ≤280 characters

Writing style:
- Be CONCISE - every word must add value
- Start with a strong hook (question, stat, or insight)
- Avoid filler words like "Learn how", "Discover", "Want to know"
- Use short, punchy sentences
- NO bullet points or numbered lists (they waste characters)
- NO reference to article title or "this article"

Professional writing principles:
- Use ACTIVE VOICE (e.g., "AI transforms businesses" not "Businesses are transformed by AI")
- NO ABBREVIATIONS or contractions (write "cannot" not "can't", "do not" not "don't")
- NO HYPHENS where avoidable (write "state of the art" not "state-of-the-art")
- SEMICOLON CAPITALIZATION: Capitalize first letter after semicolons (e.g., "Data quality matters; Clean data drives ROI")
- CONCISE SENTENCES: Avoid run-on sentences; keep sentences short and impactful

Format your response as ONLY the main tweet content (no URL, no hashtags - those are added automatically).
Do NOT include a character count, word count, labels (such as "Tweet:"), quotation marks around the tweet, code fences, or any commentary before or after the tweet text.
"""
    
    # A tweet is ~60 output tokens; 1024 leaves room without inviting rambling.
    REQUEST_PARAMS = claude_request_params(max_tokens=1024, effort="medium")

    PRIMARY_HASHTAGS = ["#AI", "#DataStrategy", "#BusinessValue"]
    SECONDARY_HASHTAGS = [
        "#MachineLearning", "#Leadership", "#TechStrategy",
        "#GenerativeAI", "#DataAnalytics", "#AIImplementation",
        "#DigitalTransformation", "#Innovation"
    ]
    
    def __init__(self, agent: Agent = None):
        """
        Initialize the Tweet Composer Agent.
        
        Args:
            agent: Optional pre-configured MCP Agent instance
        """
        if agent is None:
            # Create new agent with default configuration
            self.agent = Agent(
                name="tweet_composer",
                instruction=self.INSTRUCTION,
                server_names=[]  # No MCP servers needed for this agent
            )
        else:
            self.agent = agent
        
        self.llm = None

    async def initialize(self, model: str = None):
        """
        Initialize the LLM connection.

        Args:
            model: Optional model name override (defaults to config)
        """
        if not self.llm:
            # Attach Claude to the agent. The model comes from mcp_agent.config.yaml
            # (anthropic.default_model) unless overridden here.
            self.llm = await self.agent.attach_llm(ClaudeLLM)
            if model:
                self.llm.default_request_params.model = model
    
    def _select_hashtags(self, themes: List[str]) -> List[str]:
        """Select appropriate hashtags based on article themes."""
        # Always include #AI as primary hashtag
        hashtags = ["#AI"]

        # Add 1 secondary hashtag based on themes
        theme_keywords = ' '.join(themes).lower()

        relevant_secondary = []
        if 'machine learning' in theme_keywords or 'ml' in theme_keywords:
            relevant_secondary.append("#MachineLearning")
        if 'leadership' in theme_keywords or 'management' in theme_keywords:
            relevant_secondary.append("#Leadership")
        if 'generative' in theme_keywords or 'gpt' in theme_keywords:
            relevant_secondary.append("#GenerativeAI")
        if 'data' in theme_keywords and 'analytics' in theme_keywords:
            relevant_secondary.append("#DataAnalytics")
        if 'transform' in theme_keywords:
            relevant_secondary.append("#DigitalTransformation")
        if 'data' in theme_keywords or 'strategy' in theme_keywords:
            relevant_secondary.append("#DataStrategy")

        # If no relevant secondary hashtags found, use #DataStrategy as default
        if not relevant_secondary:
            relevant_secondary = ["#DataStrategy"]

        # Return only 2 hashtags total to save characters
        return hashtags + relevant_secondary[:1]

    # A standalone line that is length meta-commentary rather than tweet copy,
    # e.g. "(147 characters)", "Character count: 147", "147/280", "[147/280 chars]".
    # A bare number alone is NOT matched; it must carry a "chars" word or an
    # "N/M" ratio so legitimate content is never stripped.
    _META_LINE_RE = re.compile(
        r"""^[\(\[]?\s*
            (?:
                (?:character|char|word)\s*counts?\s*[:=]?\s*\d+(?:\s*/\s*\d+)?(?:\s*(?:characters?|chars?))?
              | \d+\s*/\s*\d+(?:\s*(?:characters?|chars?))?
              | \d+\s*(?:characters?|chars?)
            )
            \s*[\)\]]?\s*\.?\s*$""",
        re.IGNORECASE | re.VERBOSE,
    )

    # Length meta-commentary appended to the end of the tweet line itself,
    # e.g. "…drives ROI 🚀 (147 characters)" or "…drives ROI 🚀 (147/280)".
    _TRAILING_META_RE = re.compile(
        r"""\s*[\(\[]\s*
            (?:
                (?:character|char|word)\s*counts?\s*[:=]?\s*\d+(?:\s*/\s*\d+)?(?:\s*(?:characters?|chars?))?
              | \d+\s*/\s*\d+(?:\s*(?:characters?|chars?))?
              | \d+\s*(?:characters?|chars?)
            )
            \s*[\)\]]\s*$""",
        re.IGNORECASE | re.VERBOSE,
    )

    # Leading label the model may prepend despite instructions.
    _LEADING_LABEL_RE = re.compile(
        r"^(?:here(?:'s|\s+is)\s+(?:your|the)\s+tweet\s*[:\-]\s*|(?:your\s+)?tweet\s*[:\-]\s*)",
        re.IGNORECASE,
    )

    @classmethod
    def _sanitize_tweet_content(cls, text: str) -> str:
        """
        Strip LLM meta-commentary from a composed tweet before it is posted.

        Removes, in order: Markdown code fences, a leading "Tweet:"-style label,
        trailing standalone character-count lines, a trailing inline count
        annotation, and surrounding quotation marks. Legitimate tweet content
        (including numbers such as "10x ROI" or "80%") is left untouched.

        Args:
            text: Raw LLM response.

        Returns:
            The cleaned tweet text.
        """
        cleaned = text.strip()

        # Code fences (```lang ... ```)
        cleaned = re.sub(r'^```[a-zA-Z]*\s*\n?', '', cleaned)
        cleaned = re.sub(r'\n?```\s*$', '', cleaned)
        cleaned = cleaned.strip()

        # Leading "Tweet:" / "Here is your tweet:" label
        cleaned = cls._LEADING_LABEL_RE.sub('', cleaned).strip()

        # Trailing standalone meta lines (may be more than one)
        lines = cleaned.split('\n')
        while lines and cls._META_LINE_RE.match(lines[-1].strip()):
            lines.pop()
        cleaned = '\n'.join(lines).strip()

        # Inline trailing count annotation on the final line
        cleaned = cls._TRAILING_META_RE.sub('', cleaned).strip()

        # Surrounding quotation marks
        for open_q, close_q in (('"', '"'), ("'", "'"), ('“', '”'), ('‘', '’')):
            if len(cleaned) >= 2 and cleaned.startswith(open_q) and cleaned.endswith(close_q):
                cleaned = cleaned[1:-1].strip()
                break

        return cleaned

    def _check_grounding(self, insight: str, tweet_main_content: str) -> list:
        """
        Lightweight deterministic check that tweet content stays within the bounds
        of the source insight. No LLM call required.

        Detects two categories of likely hallucination:
          1. Numeric claims (percentages, multipliers, raw numbers) present in the
             tweet but absent from the insight string.
          2. Multi-word proper-noun phrases (Title Case sequences) present in the
             tweet but absent from the insight string.

        Args:
            insight: The single key-insight string selected for this tweet variation.
            tweet_main_content: The raw tweet text returned by the LLM, before the
                                URL and hashtags are appended.

        Returns:
            List of violation description strings. An empty list means no violations
            were detected by this heuristic pass.
        """
        violations = []
        insight_lower = insight.lower()

        # --- 1. Numeric claims ---
        # Match integers and decimals, optionally followed by a unit suffix.
        number_pattern = (
            r'\b\d+(?:\.\d+)?'
            r'(?:\s*%|\s*x|\s*times|\s*percent|\s*billion|\s*million|\s*k)?\b'
        )
        tweet_numbers = re.findall(number_pattern, tweet_main_content, re.IGNORECASE)
        insight_numbers = re.findall(number_pattern, insight, re.IGNORECASE)
        insight_numbers_lower = {n.lower() for n in insight_numbers}
        for num in tweet_numbers:
            if num.lower() not in insight_numbers_lower:
                violations.append(f"Numeric claim '{num}' not found in source insight")

        # --- 2. Multi-word proper-noun phrases ---
        # Heuristic: two or more consecutive capitalised tokens (e.g. "McKinsey Research",
        # "Harvard Business School", "Andrew Ng"). Using [A-Za-z]+ after the leading
        # uppercase letter handles mixed-case proper names such as "McKinsey" (internal K)
        # and two-letter surnames like "Ng". Single capitalised words are excluded to
        # avoid flagging sentence-initial words.
        proper_nouns = re.findall(
            r'\b(?:[A-Z][A-Za-z]+)(?:\s+[A-Z][A-Za-z]+)+\b',
            tweet_main_content
        )
        for noun in proper_nouns:
            if noun.lower() not in insight_lower:
                violations.append(f"Proper noun phrase '{noun}' not found in source insight")

        return violations

    async def compose_tweet(
        self,
        article_title: str,
        article_url: str,
        insights: List[str],
        themes: List[str],
        variation_number: int,
        focus_theme: str = "general",
        used_insights: List[str] = None
    ) -> tuple[str, List[str]]:
        """
        Compose a single tweet variation.

        Args:
            article_title: Title of the article (NOT used in tweet content)
            article_url: URL to the article
            insights: List of key insights to choose from
            themes: Article themes
            variation_number: Which variation this is (1-4)
            focus_theme: Theme to focus on for this variation
            used_insights: List of insights already used in previous variations

        Returns:
            Tuple of (composed tweet text, list of insights used)
        """
        # Ensure LLM is initialized
        if not self.llm:
            await self.initialize()
        
        # Initialize used_insights if not provided
        if used_insights is None:
            used_insights = []

        # Select ONE unique insight for this variation that hasn't been used
        available_insights = [ins for ins in insights if ins not in used_insights]
        if not available_insights:
            # If all insights used, start over but try to use different combinations
            available_insights = insights

        # Select the insight for this variation based on variation number
        insight_index = (variation_number - 1) % len(available_insights)
        selected_insight = available_insights[insight_index]

        # Select hashtags
        hashtags = self._select_hashtags(themes)
        hashtag_str = ' '.join(hashtags)

        # Calculate available characters for main content
        # Twitter shortens ALL URLs to 23 characters (t.co format)
        url_length = 23  # Twitter's t.co shortened URL length
        hashtag_length = len(hashtag_str)
        spacing = 4  # 2 newlines before URL, 2 newlines before hashtags

        # Available chars for main content (with aggressive safety buffer)
        available_chars = 280 - url_length - hashtag_length - spacing - 35  # 35 char safety buffer

        # Create composition prompt with strict character limit
        # DO NOT include article title in prompt
        prompt = f"""Create an ULTRA-CONCISE tweet highlighting this key insight.

Key Insight to Feature:
{selected_insight}

ABSOLUTE REQUIREMENTS:
- Variation #{variation_number} - make it UNIQUE from other variations
- Focus: {focus_theme}
- DO NOT mention or reference the article title
- Extract the STRATEGIC VALUE of this insight
- MAX LENGTH: {available_chars} characters (STRICTLY ENFORCED)
- Use 1 emoji only (🎯, 💡, 🚀, 📊, ⚡, 🔍)
- Cut ALL filler words ("Learn", "Discover", "Want to", "This article", etc.)
- NO explanations, NO fluff
- Make it thought-provoking and actionable
- STRICTLY GROUNDED: Express ONLY what is stated in the Key Insight above. Do NOT add statistics, expert quotes, external context, or claims not present in the provided insight. Every assertion in the tweet must be directly supported by the insight text.
- NO HALLUCINATION: Do not embellish, invent numbers, or introduce details beyond what the insight contains. Distil and rephrase compellingly — do not create new information.

PROFESSIONAL WRITING RULES:
- Use ACTIVE VOICE only (subject performs action)
- NO contractions (write "cannot" not "can't", "do not" not "don't")
- NO hyphens where avoidable (write "real time" not "real-time")
- Capitalize after semicolons; Start new clause with capital letter
- Keep sentences short and punchy

EXAMPLES OF HIGH-LEVEL INSIGHT TWEETS (following professional writing principles):
"AI success = 80% org readiness, 20% tech 🚀 Organizations drive implementation through cultural alignment"
"Strategic fit beats technical sophistication 💡 Match AI approach to business problem, not hype"
"Data quality compounds over time 📊 Clean data delivers 10x ROI versus complex models on messy data"

OUTPUT FORMAT:
- Return ONLY the tweet text itself
- Do NOT include a character count, word count, or length annotation of any kind
- Do NOT wrap the tweet in quotation marks or code fences
- Do NOT add labels (such as "Tweet:") or commentary before or after the tweet

YOUR TWEET (MAX {available_chars} chars):
"""

        # Get tweet content from LLM using MCP Agent framework with timeout
        print(f"🔍 Calling Anthropic API (model: {self.llm.model})")
        print(f"🔍 Prompt length: {len(prompt)} characters")

        try:
            # Add 90-second timeout to prevent hanging
            tweet_content = await asyncio.wait_for(
                self.llm.generate_str(message=prompt, request_params=self.REQUEST_PARAMS),
                timeout=90.0
            )
            raw_response = tweet_content.strip()
            tweet_content = self._sanitize_tweet_content(raw_response)
            print(f"✅ Received response: {len(tweet_content)} characters")
            if tweet_content != raw_response:
                print(f"🧹 Sanitized LLM meta-commentary out of tweet content "
                      f"({len(raw_response)} -> {len(tweet_content)} chars)")

            # Grounding check: warn if the tweet introduces claims absent from the source insight
            grounding_violations = self._check_grounding(selected_insight, tweet_content)
            if grounding_violations:
                print(f"⚠️  Grounding warnings for variation #{variation_number} "
                      f"(insight: '{selected_insight[:60]}...'):")
                for violation in grounding_violations:
                    print(f"   - {violation}")

        except asyncio.TimeoutError:
            error_msg = "⚠️  LLM request timed out after 90 seconds. Please check:\n" \
                       "   1. Anthropic API key is valid\n" \
                       "   2. Network connectivity to api.anthropic.com\n" \
                       "   3. No firewall blocking the connection"
            print(error_msg)
            raise Exception("Tweet composition timed out - API not responding")
        except Exception as e:
            error_msg = f"❌ Error calling Anthropic API: {str(e)}"
            print(error_msg)
            raise

        # Enforce character limit on main content
        if len(tweet_content) > available_chars:
            # Truncate and add ellipsis
            tweet_content = tweet_content[:available_chars-1].rsplit(' ', 1)[0] + '…'
            print(f"⚠️  Warning: Tweet content truncated to {available_chars} chars")

        # Assemble full tweet
        full_tweet = f"{tweet_content}\n\n{article_url}\n\n{hashtag_str}"

        # Calculate effective character count (Twitter shortens URLs to 23 chars)
        effective_char_count = len(tweet_content) + 23 + len(hashtag_str) + 4

        # Final validation
        if effective_char_count > 280:
            print(f"⚠️  Warning: Effective tweet length is {effective_char_count} chars (exceeds 280)")
            print(f"   Content: {len(tweet_content)}, URL: 23 (shortened), Hashtags: {len(hashtag_str)}, Spacing: 4")

        # Return tweet and the insight used
        return full_tweet, [selected_insight]

    async def compose_multiple_variations(
        self,
        article_number: int,
        article_title: str,
        article_url: str,
        insights: List[str],
        themes: List[str],
        num_variations: int = 4
    ) -> List[Tweet]:
        """
        Compose multiple tweet variations for an article.
        Each variation highlights a DIFFERENT key insight.

        Args:
            article_number: Article number
            article_title: Title of the article (NOT used in tweet content)
            article_url: URL to the article
            insights: List of key insights (should have at least num_variations insights)
            themes: Article themes
            num_variations: Number of variations to create (default: 4)

        Returns:
            List of Tweet objects, each featuring a different insight
        """
        tweets = []
        used_insights = []  # Track insights used across variations

        # Define focus themes for variations
        focus_themes = [
            "strategic_value",
            "systematic_approach",
            "practical_application",
            "expert_insights"
        ]

        # Ensure we have enough insights
        if len(insights) < num_variations:
            print(f"⚠️  Warning: Only {len(insights)} insights available for {num_variations} variations")

        for i in range(num_variations):
            focus = focus_themes[i] if i < len(focus_themes) else "general"

            # Compose tweet with unique insight
            tweet_content, insights_used_in_tweet = await self.compose_tweet(
                article_title=article_title,
                article_url=article_url,
                insights=insights,
                themes=themes,
                variation_number=i + 1,
                focus_theme=focus,
                used_insights=used_insights
            )

            # Track used insights to ensure uniqueness
            used_insights.extend(insights_used_in_tweet)

            # Extract hashtags from tweet
            hashtags = [word for word in tweet_content.split() if word.startswith('#')]

            # Calculate effective character count (Twitter shortens URLs to 23 chars)
            # Extract content before URL
            content_parts = tweet_content.split('\n\n')
            main_content = content_parts[0] if content_parts else tweet_content
            hashtag_str = ' '.join(hashtags)
            effective_count = len(main_content) + 23 + len(hashtag_str) + 4

            tweet = Tweet(
                article_number=article_number,
                variation_number=i + 1,
                content=tweet_content,
                character_count=effective_count,  # Use effective count, not full length
                hashtags=hashtags,
                insights_used=insights_used_in_tweet,
                focus_theme=focus
            )

            tweets.append(tweet)

        return tweets


# Standalone function for use in workflows
async def compose_tweets_for_article(
    article_number: int,
    article_title: str,
    article_url: str,
    insights: List[str],
    themes: List[str],
    num_variations: int = 4,
    agent: Agent = None
) -> List[Dict[str, Any]]:
    """
    Compose multiple tweet variations for an article.

    Args:
        article_number: Article number
        article_title: Title of the article
        article_url: URL to the article
        insights: List of key insights extracted from the article
        themes: Article themes
        num_variations: Number of tweet variations to create
        agent: Optional pre-configured MCP Agent instance

    Returns:
        List of tweet dictionaries
    """
    composer = MCPTweetComposerAgent(agent=agent)
    await composer.initialize()
    tweets = await composer.compose_multiple_variations(
        article_number=article_number,
        article_title=article_title,
        article_url=article_url,
        insights=insights,
        themes=themes,
        num_variations=num_variations,
    )

    return [
        {
            "article_number": tweet.article_number,
            "variation_number": tweet.variation_number,
            "content": tweet.content,
            "character_count": tweet.character_count,
            "hashtags": tweet.hashtags,
            "insights_used": tweet.insights_used,
            "focus_theme": tweet.focus_theme,
        }
        for tweet in tweets
    ]