"""
Tweet Processor Workflow - MCP Agent Cloud Implementation
Main orchestration workflow using LastMile AI's MCP Agent Cloud framework.
"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime, timedelta
import json
import sys
import os
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
import logging

# Load environment variables BEFORE importing MCP Agent
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# MCP Agent Cloud imports
from mcp_agent.app import MCPApp
from mcp_agent.agents.agent import Agent

# Import MCP-based agents
from agents.mcp_content_analyzer_agent import MCPContentAnalyzerAgent, analyze_article_content
from agents.mcp_tweet_composer_agent import MCPTweetComposerAgent, compose_tweets_for_article

# Configuration
DOCUMENT_ID = "your_google_drive_document_id_here"
POSTING_SCHEDULE = {
    "day": "Thursday",
    "time": "11:30",
    "timezone": "America/New_York"
}


class MCPTweetProcessorWorkflow:
    """Main workflow for processing newsletter articles using MCP Agent Cloud."""

    # Note: URL validation now uses format patterns instead of exact matching
    # This allows flexibility while ensuring URLs follow expected LinkedIn pulse patterns

    def __init__(self, document_id: str = DOCUMENT_ID, mcp_app: MCPApp = None):
        """
        Initialize the workflow.

        Args:
            document_id: Google Drive document ID
            mcp_app: Optional MCPApp instance (created if not provided)
        """
        self.document_id = document_id
        self.state = self._load_state()

        # Create MCP App if not provided
        if mcp_app is None:
            self.mcp_app = MCPApp(name="tweet_processor")
        else:
            self.mcp_app = mcp_app

        # Agents will be initialized in async context
        self.content_analyzer = None
        self.tweet_composer = None

        # Setup logging
        self.logger = logging.getLogger(__name__)

    def validate_article_url(self, article_number: int, article_url: str) -> bool:
        """
        Validate that the URL format is appropriate for the specified article number.

        This method validates URL format patterns instead of requiring exact matches,
        which allows for flexibility while ensuring URLs follow expected patterns.

        Args:
            article_number: The article number (1-5)
            article_url: The URL to validate

        Returns:
            bool: True if URL format is valid for the article

        Raises:
            ValueError: If validation fails
        """
        # Check if article number is valid
        if article_number not in range(1, 6):
            raise ValueError(f"Invalid article number: {article_number}. Must be 1-5.")

        # Article #5 is allowed to have no URL (incomplete in document)
        if article_number == 5 and (not article_url or not article_url.strip()):
            self.logger.info(f"✅ Article #{article_number} has no URL (expected for incomplete article)")
            return True

        # For other articles, URL is required
        if not article_url or not article_url.strip():
            raise ValueError(f"Article #{article_number} has empty or None URL")

        # Validate URL format using the existing validate_url_format method
        # This checks for proper LinkedIn pulse URL patterns
        try:
            self.validate_url_format(article_url, article_number)
            self.logger.info(f"✅ URL format validation passed for Article #{article_number}: {article_url}")
            return True
        except ValueError as e:
            self.logger.error(f"❌ URL format validation failed for Article #{article_number}: {article_url}")
            raise e

    def validate_url_format(self, url: str, article_number: int = None) -> bool:
        """
        Validate URL format and structure.

        Args:
            url: URL to validate
            article_number: Optional article number for error messages

        Returns:
            bool: True if URL format is valid

        Raises:
            ValueError: If URL format is invalid
        """
        article_ref = f"Article #{article_number}" if article_number else "URL"

        if not url or not url.strip():
            raise ValueError(f"{article_ref} has empty URL")

        if not url.startswith('https://'):
            raise ValueError(f"{article_ref} URL must start with https://")

        if 'linkedin.com/pulse/' not in url:
            raise ValueError(f"{article_ref} URL must be a LinkedIn pulse URL")

        # Check for valid ending patterns (LinkedIn pulse URLs end with author identifier)
        # Pattern: ends with '-lim-' followed by alphanumeric characters and '/'
        import re
        if not re.search(r'-lim-[a-zA-Z0-9]+/$', url):
            raise ValueError(f"{article_ref} URL must end with LinkedIn author pattern (-lim-xxxxx/)")

        return True

    def log_url_validation_report(self, articles: List[Dict[str, Any]]) -> None:
        """
        Log a comprehensive URL validation report.

        Args:
            articles: List of article data
        """
        self.logger.info("=" * 60)
        self.logger.info("URL VALIDATION REPORT")
        self.logger.info("=" * 60)

        for article in articles:
            article_number = article['number']
            article_url = article['url']
            article_title = article.get('title', 'Unknown')

            self.logger.info(f"Article #{article_number}: {article_title}")
            self.logger.info(f"  URL: {article_url}")

            try:
                self.validate_url_format(article_url, article_number)
                self.validate_article_url(article_number, article_url)
                self.logger.info(f"  Status: ✅ VALID")
            except ValueError as e:
                self.logger.error(f"  Status: ❌ INVALID - {str(e)}")

            self.logger.info("")

        self.logger.info("=" * 60)

    def _validate_articles_data(self, articles: List[Dict[str, Any]]) -> None:
        """
        Validate article data integrity including URLs.

        Args:
            articles: List of article data to validate

        Raises:
            ValueError: If validation fails
        """
        if not articles:
            raise ValueError("No articles found in data")

        # Filter to only the first 5 articles (the system is designed for 5 articles)
        if len(articles) < 5:
            raise ValueError(f"Expected at least 5 articles, found {len(articles)}")

        # Use only the first 5 articles
        articles = articles[:5]

        # Check for required fields and URL validation
        for article in articles:
            article_number = article.get('number')
            article_url = article.get('url')
            article_title = article.get('title')

            # Check required fields
            if not article_number:
                raise ValueError(f"Article missing 'number' field: {article}")

            if not article_title:
                raise ValueError(f"Article #{article_number} missing 'title' field")

            # Article #5 is allowed to have no URL (incomplete in document)
            if not article_url and article_number != 5:
                raise ValueError(f"Article #{article_number} missing 'url' field")

            # Validate URL format and mapping (only if URL exists)
            if article_url:
                try:
                    self.validate_url_format(article_url, article_number)
                    self.validate_article_url(article_number, article_url)
                except ValueError as e:
                    raise ValueError(f"Article #{article_number} validation failed: {str(e)}")
            elif article_number == 5:
                # Article #5 has no URL - this is expected
                self.logger.info(f"Article #{article_number} has no URL (incomplete article)")
            else:
                raise ValueError(f"Article #{article_number} missing 'url' field")

        # Check for duplicate article numbers
        article_numbers = [article['number'] for article in articles]
        if len(set(article_numbers)) != len(article_numbers):
            raise ValueError(f"Duplicate article numbers found: {article_numbers}")

        # Check for duplicate URLs
        article_urls = [article['url'] for article in articles]
        if len(set(article_urls)) != len(article_urls):
            raise ValueError(f"Duplicate URLs found: {article_urls}")

        # Log validation report
        self.log_url_validation_report(articles)

    def _load_state(self) -> Dict[str, Any]:
        """Load workflow state from storage."""
        try:
            with open('workflow_state.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "current_article": 1,
                "current_variation": 1,
                "last_posted": None,
                "total_posts": 0,
                "articles_cache": []
            }
    
    def _save_state(self):
        """Save workflow state to storage."""
        with open('workflow_state.json', 'w') as f:
            json.dump(self.state, f, indent=2)
    
    async def initialize_agents(self):
        """Initialize MCP agents."""
        # Create Content Analyzer Agent
        analyzer_agent = Agent(
            name="content_analyzer",
            instruction=MCPContentAnalyzerAgent.INSTRUCTION,
            server_names=[]  # No MCP servers needed
        )
        self.content_analyzer = MCPContentAnalyzerAgent(agent=analyzer_agent)
        await self.content_analyzer.initialize()
        
        # Create Tweet Composer Agent
        composer_agent = Agent(
            name="tweet_composer",
            instruction=MCPTweetComposerAgent.INSTRUCTION,
            server_names=[]  # No MCP servers needed
        )
        self.tweet_composer = MCPTweetComposerAgent(agent=composer_agent)
        await self.tweet_composer.initialize()
    
    async def run_weekly_post(self, post_to_twitter: bool = False) -> Dict[str, Any]:
        """
        Execute the weekly tweet posting workflow.
        
        Args:
            post_to_twitter: Whether to actually post to Twitter (vs simulation)
        
        Returns:
            Result dictionary with status and details
        """
        print(f"🚀 Starting Tweet Processor Workflow (MCP Agent Cloud)")
        print(f"📅 Timestamp: {datetime.now().isoformat()}")
        print()
        
        try:
            # Initialize MCP App and agents
            async with self.mcp_app.run() as mcp_agent_app:
                logger = mcp_agent_app.logger
                logger.info("MCP Agent Cloud initialized")
                
                # Initialize agents
                await self.initialize_agents()
                logger.info("Agents initialized")
                
                # Step 1: Read and parse document (if not cached)
                if not self.state.get("articles_cache"):
                    print("📄 Step 1: Reading document from Google Drive...")
                    articles = await self._read_and_parse_document()

                    # Validate URLs before caching
                    print("🔍 Validating article URLs...")
                    try:
                        self._validate_articles_data(articles)
                        print("✅ All article URLs validated successfully")
                        self.logger.info("Article URL validation passed")
                    except ValueError as e:
                        error_msg = f"Article validation failed: {str(e)}"
                        print(f"❌ {error_msg}")
                        self.logger.error(error_msg)
                        raise

                    self.state["articles_cache"] = articles
                    self._save_state()
                    print(f"✓ Found {len(articles)} articles")
                    logger.info(f"Loaded {len(articles)} articles from Google Drive")
                else:
                    articles = self.state["articles_cache"]
                    print(f"✓ Using cached articles ({len(articles)} total)")
                    logger.info(f"Using cached articles: {len(articles)} total")

                    # Validate cached articles
                    try:
                        self._validate_articles_data(articles)
                        self.logger.info("Cached article URL validation passed")
                    except ValueError as e:
                        error_msg = f"Cached article validation failed: {str(e)}"
                        self.logger.error(error_msg)
                        print(f"⚠️ Warning: {error_msg}")
                        # Don't raise here as we want to continue with cached data

                print()
                
                # Step 2: Get current article to post
                current_article_num = self.state["current_article"]
                current_variation = self.state["current_variation"]
                
                print(f"📝 Step 2: Processing Article #{current_article_num}, Variation {current_variation}")
                logger.info(f"Processing Article #{current_article_num}, Variation {current_variation}")
                
                article = next((a for a in articles if a["number"] == current_article_num), None)
                if not article:
                    raise ValueError(f"Article #{current_article_num} not found")
                
                print(f"   Title: {article['title'][:60]}...")
                print()
                
                # Step 3: Analyze article content (if not cached)
                cache_key = f"analysis_{current_article_num}"
                if cache_key not in self.state:
                    print("🔍 Step 3: Analyzing article content with MCP Agent...")
                    logger.info("Starting article analysis")
                    
                    # Use MCP Content Analyzer Agent
                    insights = await self.content_analyzer.analyze_article(article)
                    
                    analysis = {
                        'article_number': insights.article_number,
                        'article_title': insights.article_title,
                        'article_url': insights.article_url,
                        'key_insights': insights.key_insights,
                        'themes': insights.themes,
                        'expert_references': insights.expert_references,
                        'frameworks_mentioned': insights.frameworks_mentioned
                    }
                    
                    self.state[cache_key] = analysis
                    self._save_state()
                    print(f"✓ Extracted {len(analysis['key_insights'])} key insights")
                    logger.info(f"Analysis complete: {len(analysis['key_insights'])} insights extracted")
                else:
                    analysis = self.state[cache_key]
                    print(f"✓ Using cached analysis ({len(analysis['key_insights'])} insights)")
                    logger.info("Using cached analysis")
                print()
                
                # Step 4: Generate tweet for current variation
                print(f"🐦 Step 4: Composing tweet with MCP Agent (Variation {current_variation})...")
                logger.info(f"Composing tweet variation {current_variation}")

                # URL Validation before tweet composition
                article_number = article['number']
                article_url = article['url']

                print(f"🔍 Validating URL for Article #{article_number}...")
                self.logger.info(f"Processing Article #{article_number} with URL: {article_url}")

                try:
                    # Validate URL format and mapping
                    self.validate_url_format(article_url, article_number)
                    self.validate_article_url(article_number, article_url)

                    # Cross-validate with analysis cache if available
                    if cache_key in self.state:
                        analysis_url = self.state[cache_key].get('article_url')
                        if analysis_url and analysis_url != article_url:
                            raise ValueError(
                                f"URL mismatch detected for Article #{article_number}:\n"
                                f"Article cache URL: {article_url}\n"
                                f"Analysis cache URL: {analysis_url}\n"
                                f"These URLs must match for data integrity."
                            )

                    print(f"✅ URL validation passed for Article #{article_number}")

                except ValueError as e:
                    error_msg = f"URL validation failed for Article #{article_number}: {str(e)}"
                    self.logger.error(error_msg)
                    print(f"❌ {error_msg}")
                    raise

                # Use MCP Tweet Composer Agent
                tweets = await self.tweet_composer.compose_multiple_variations(
                    article_number=article_number,
                    article_title=article['title'],
                    article_url=article_url,
                    insights=analysis['key_insights'],
                    themes=analysis.get('themes', []),
                    num_variations=4
                )
                
                # Get the specific variation
                tweet_obj = tweets[current_variation - 1]
                tweet = {
                    'article_number': tweet_obj.article_number,
                    'variation_number': tweet_obj.variation_number,
                    'content': tweet_obj.content,
                    'character_count': tweet_obj.character_count,
                    'hashtags': tweet_obj.hashtags,
                    'insights_used': tweet_obj.insights_used
                }
                
                print(f"✓ Tweet composed ({tweet['character_count']} characters)")
                logger.info(f"Tweet composed: {tweet['character_count']} chars")
                print()
                print("   Preview:")
                for line in tweet['content'].split('\n'):
                    print(f"   {line}")
                print()
                
                # Step 5: Post tweet to Twitter/X
                if post_to_twitter:
                    print("📤 Step 5: Posting tweet to Twitter/X...")
                    print("   [LIVE] Posting to Twitter API...")
                    logger.info("Posting tweet to Twitter")
                    
                    from mcp_servers.twitter_server import TwitterClient
                    twitter_client = TwitterClient()
                    result = twitter_client.post_tweet(tweet['content'])
                    
                    if result.get('tweet_id'):
                        print(f"✓ Tweet posted successfully!")
                        print(f"   Tweet ID: {result['tweet_id']}")
                        print(f"   URL: https://twitter.com/user/status/{result['tweet_id']}")
                        logger.info(f"Tweet posted successfully: {result['tweet_id']}")
                        
                        post_result = {
                            'success': True,
                            'tweet_id': result['tweet_id'],
                            'url': f"https://twitter.com/user/status/{result['tweet_id']}",
                            'posted_at': result['posted_at']
                        }
                        
                        # Update workflow state
                        self.state["last_posted"] = datetime.now().isoformat()
                        self.state["total_posts"] += 1
                        self._update_state_after_post(articles)
                    else:
                        raise Exception("Failed to post tweet")
                else:
                    print("📤 Step 5: Simulating tweet post (ENABLE_TWITTER_POSTING=false)...")
                    print("   [SIMULATION] Tweet would be posted to Twitter API")
                    logger.info("Tweet posting simulated")
                    
                    post_result = {
                        'success': True,
                        'tweet_id': 'simulated',
                        'url': 'simulated',
                        'posted_at': datetime.now().isoformat(),
                        'simulated': True
                    }
                print()
                
                # Step 6: Update state for next run (only if actually posted)
                if post_to_twitter:
                    print("💾 Step 6: Updating workflow state...")
                    print(f"✓ Next post: Article #{self.state['current_article']}, Variation {self.state['current_variation']}")
                    logger.info(f"State updated: Next Article #{self.state['current_article']}, Variation {self.state['current_variation']}")
                else:
                    print("💾 Step 6: State not updated (simulation mode)")
                    logger.info("State not updated (simulation mode)")
                print()
                
                result = {
                    "status": "success",
                    "article_number": current_article_num,
                    "variation_number": current_variation,
                    "tweet": tweet,
                    "post_result": post_result,
                    "next_article": self.state["current_article"],
                    "next_variation": self.state["current_variation"],
                    "timestamp": datetime.now().isoformat(),
                    "mcp_agent_cloud": True
                }
                
                print("✅ Workflow completed successfully!")
                logger.info("Workflow completed successfully")
                return result
                
        except Exception as e:
            print(f"❌ Workflow failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def _read_and_parse_document(self) -> List[Dict[str, Any]]:
        """Read and parse the newsletter document."""
        # Check if we should use real APIs or mocks
        use_real_apis = os.getenv('USE_REAL_APIS', 'false').lower() == 'true'

        if use_real_apis:
            # Use real Google Drive API
            from mcp_servers.google_drive_server import GoogleDriveClient, DocumentParser

            client = GoogleDriveClient()
            text = client.read_document_text(self.document_id)
            parser = DocumentParser(text)
            articles = parser.parse()

            # Convert to dict format and filter to first 5 articles
            articles_data = [
                {
                    'number': a.number,
                    'title': a.title,
                    'url': a.url,
                    'content': a.content,
                    'word_count': a.word_count,
                    'has_title': a.has_title,
                    'has_url': a.has_url
                }
                for a in articles
            ]

            # Return only the first 5 articles (system is designed for 5 articles)
            return articles_data[:5]
        else:
            # Use mock for testing
            from test_system import MockDocumentParser, SAMPLE_DOCUMENT
            parser = MockDocumentParser(SAMPLE_DOCUMENT)
            articles = parser.parse()
            return articles

    def _update_state_after_post(self, articles: List[Dict[str, Any]]):
        """Update workflow state after posting a tweet."""
        current_article = self.state["current_article"]
        current_variation = self.state["current_variation"]

        # Move to next variation
        if current_variation < 4:
            self.state["current_variation"] = current_variation + 1
        else:
            # Move to next article
            self.state["current_variation"] = 1
            if current_article < len(articles):
                self.state["current_article"] = current_article + 1
            else:
                # Cycle back to first article
                self.state["current_article"] = 1

        self._save_state()

    async def generate_pipeline_preview(self, weeks: int = 3) -> List[Dict[str, Any]]:
        """
        Generate a preview of upcoming tweets for the next N weeks.

        Args:
            weeks: Number of weeks to preview

        Returns:
            List of tweet previews with scheduling information
        """
        print(f"📅 Generating {weeks}-week pipeline preview...")
        print()

        # Initialize MCP App and agents
        async with self.mcp_app.run() as mcp_agent_app:
            logger = mcp_agent_app.logger
            logger.info(f"Generating {weeks}-week pipeline preview")

            # Initialize agents
            await self.initialize_agents()

            # Load articles
            if not self.state.get("articles_cache"):
                articles = await self._read_and_parse_document()
                self.state["articles_cache"] = articles
                self._save_state()
            else:
                articles = self.state["articles_cache"]

            # Get posting schedule
            posting_day = os.getenv('POSTING_DAY', 'Thursday')
            posting_time = os.getenv('POSTING_TIME', '11:30')
            posting_timezone = os.getenv('POSTING_TIMEZONE', 'America/New_York')

            # Calculate next posting date
            tz = ZoneInfo(posting_timezone)
            now = datetime.now(tz)

            # Find next occurrence of posting day
            days_ahead = (self._day_to_number(posting_day) - now.weekday()) % 7
            if days_ahead == 0 and now.time() > datetime.strptime(posting_time, '%H:%M').time():
                days_ahead = 7

            next_post_date = now + timedelta(days=days_ahead)
            hour, minute = map(int, posting_time.split(':'))
            next_post_date = next_post_date.replace(hour=hour, minute=minute, second=0, microsecond=0)

            # Generate preview for N weeks
            pipeline = []
            current_article_num = self.state["current_article"]
            current_variation = self.state["current_variation"]

            for week in range(weeks):
                post_date = next_post_date + timedelta(weeks=week)

                # Get article
                article = next((a for a in articles if a["number"] == current_article_num), None)
                if not article:
                    break

                # Analyze article (use cache if available)
                cache_key = f"analysis_{current_article_num}"
                if cache_key in self.state:
                    analysis = self.state[cache_key]
                else:
                    insights = await self.content_analyzer.analyze_article(article)
                    analysis = {
                        'article_number': insights.article_number,
                        'article_title': insights.article_title,
                        'article_url': insights.article_url,
                        'key_insights': insights.key_insights,
                        'themes': insights.themes,
                        'expert_references': insights.expert_references,
                        'frameworks_mentioned': insights.frameworks_mentioned
                    }
                    self.state[cache_key] = analysis
                    self._save_state()

                # URL Validation before tweet composition
                article_number = article['number']
                article_url = article['url']

                self.logger.info(f"Processing Article #{article_number} with URL: {article_url}")

                try:
                    # Validate URL format and mapping
                    self.validate_url_format(article_url, article_number)
                    self.validate_article_url(article_number, article_url)

                    # Cross-validate with analysis cache
                    analysis_url = analysis.get('article_url')
                    if analysis_url and analysis_url != article_url:
                        raise ValueError(
                            f"URL mismatch detected for Article #{article_number}:\n"
                            f"Article cache URL: {article_url}\n"
                            f"Analysis cache URL: {analysis_url}\n"
                            f"These URLs must match for data integrity."
                        )

                    self.logger.info(f"✅ URL validation passed for Article #{article_number}")

                except ValueError as e:
                    error_msg = f"URL validation failed for Article #{article_number}: {str(e)}"
                    self.logger.error(error_msg)
                    raise

                # Compose tweet
                tweets = await self.tweet_composer.compose_multiple_variations(
                    article_number=article_number,
                    article_title=article['title'],
                    article_url=article_url,
                    insights=analysis['key_insights'],
                    themes=analysis.get('themes', []),
                    num_variations=4
                )

                tweet_obj = tweets[current_variation - 1]

                pipeline.append({
                    'week': week + 1,
                    'post_date': post_date.isoformat(),
                    'article_number': current_article_num,
                    'variation_number': current_variation,
                    'article_title': article['title'],
                    'tweet_content': tweet_obj.content,
                    'character_count': tweet_obj.character_count
                })

                # Move to next variation/article
                if current_variation < 4:
                    current_variation += 1
                else:
                    current_variation = 1
                    if current_article_num < len(articles):
                        current_article_num += 1
                    else:
                        current_article_num = 1

            logger.info(f"Pipeline preview generated: {len(pipeline)} weeks")
            return pipeline

    def _day_to_number(self, day_name: str) -> int:
        """Convert day name to number (0=Monday, 6=Sunday)."""
        days = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        return days.get(day_name.lower(), 3)  # Default to Thursday

