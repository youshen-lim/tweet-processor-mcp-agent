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
DOCUMENT_ID = None  # Legacy constant - no longer used (migrated to local file storage)
POSTING_SCHEDULE = {
    "day": "Monday",
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
            document_id: (Deprecated) Legacy parameter, no longer used
            mcp_app: Optional MCPApp instance (created if not provided)
        """
        # Legacy parameter kept for backward compatibility but not used
        self.articles_file = os.getenv('ARTICLES_FILE', 'data/articles.md')
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
            article_number: The article number (any positive integer)
            article_url: The URL to validate

        Returns:
            bool: True if URL format is valid for the article

        Raises:
            ValueError: If validation fails
        """
        # Check if article number is valid (any positive integer)
        if not isinstance(article_number, int) or article_number < 1:
            raise ValueError(f"Invalid article number: {article_number}. Must be a positive integer.")

        # Some articles may be incomplete and have no URL (like Article #6)
        if not article_url or not article_url.strip():
            self.logger.info(f"⚠️  Article #{article_number} has no URL (incomplete article)")
            raise ValueError(f"Article #{article_number} has empty URL")

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

        # Filter to only articles with content (skip incomplete articles like Article #6)
        articles_with_content = [a for a in articles if a.get('word_count', 0) > 0 and a.get('has_url', False)]

        if not articles_with_content:
            raise ValueError("No articles with content found in data")

        self.logger.info(f"Found {len(articles)} total articles, {len(articles_with_content)} with content")

        # Use articles with content for validation
        articles = articles_with_content

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

            # All articles in the validation set should have URLs (we filtered out incomplete ones)
            if not article_url:
                raise ValueError(f"Article #{article_number} missing 'url' field")

            # Validate URL format and mapping
            try:
                self.validate_url_format(article_url, article_number)
                self.validate_article_url(article_number, article_url)
            except ValueError as e:
                raise ValueError(f"Article #{article_number} validation failed: {str(e)}")

        # Check for duplicate article numbers
        article_numbers = [article['number'] for article in articles]
        if len(set(article_numbers)) != len(article_numbers):
            raise ValueError(f"Duplicate article numbers found: {article_numbers}")

        # Check for duplicate URLs and warn (but don't fail)
        article_urls = [article['url'] for article in articles]
        unique_urls = set(article_urls)
        if len(unique_urls) != len(article_urls):
            duplicate_urls = [url for url in article_urls if article_urls.count(url) > 1]
            duplicate_articles = [f"#{a['number']}" for a in articles if a['url'] in duplicate_urls]
            self.logger.warning(f"Duplicate URLs detected for articles {duplicate_articles}: {list(set(duplicate_urls))}")
            print(f"⚠️ Warning: Duplicate URLs found for articles {duplicate_articles}")
            print("   System will use the first occurrence of each URL for processing")

        # Log validation report
        self.log_url_validation_report(articles)

    def _append_tweet_audit(self, event: str, tweet: Dict[str, Any], tweet_id: str = None):
        """
        Append the full tweet text to logs/tweet_audit.log.

        Plain-text and written synchronously: the mcp_agent JSONL file transport
        drops events emitted near the end of a run (the app shuts down before
        the transport flushes), so this file is the reliable record of what was
        composed and what was actually posted.
        """
        try:
            os.makedirs('logs', exist_ok=True)
            header = (
                f"[{datetime.now().isoformat()}] {event.upper()} "
                f"article=#{tweet['article_number']} "
                f"variation={tweet['variation_number']} "
                f"chars={tweet['character_count']}"
            )
            if tweet_id:
                header += f" tweet_id={tweet_id}"
            with open(os.path.join('logs', 'tweet_audit.log'), 'a', encoding='utf-8') as f:
                f.write(header + "\n")
                f.write(tweet['content'] + "\n")
                f.write("-" * 60 + "\n")
        except Exception as e:
            self.logger.warning(f"Failed to write tweet audit log: {e}")

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

    def _sync_articles_if_docx_newer(self):
        """Defense-in-depth (Option B): regenerate articles.md from articles.docx
        when the .docx is newer, even if the scheduled .bat sync step (Option A)
        did not run -- e.g. when invoked directly via `python run_tweet_processor.py`,
        if the .bat sync line was removed, or if the wrong entry point was scheduled.

        This is idempotent with Option A: after either path runs, articles.md is
        newer than articles.docx, so this becomes a no-op. It is fail-open -- any
        error (missing python-docx, unparseable .docx, locked file) is logged and
        the existing last-good articles.md is left untouched so posting proceeds.
        """
        from pathlib import Path
        try:
            docx_path = Path('data/articles.docx')
            md_path = Path(self.articles_file)

            if not docx_path.exists():
                return  # no source document to sync from
            if md_path.exists() and docx_path.stat().st_mtime <= md_path.stat().st_mtime:
                return  # articles.md already up to date -> no-op

            # Lazily import the converter from scripts/ (keeps src/ decoupled).
            scripts_dir = os.path.abspath(
                os.path.join(os.path.dirname(__file__), '..', '..', 'scripts')
            )
            if scripts_dir not in sys.path:
                sys.path.insert(0, scripts_dir)
            from convert_docx_to_md import parse_docx, build_markdown

            articles = parse_docx(docx_path)
            if not articles:
                self.logger.warning(
                    "docx auto-sync: no articles parsed; keeping existing articles.md"
                )
                return

            # Atomic write so a failure can never leave a truncated articles.md.
            markdown = build_markdown(articles)
            tmp_path = md_path.with_suffix(md_path.suffix + '.tmp')
            tmp_path.write_text(markdown, encoding='utf-8')
            os.replace(tmp_path, md_path)

            # Invalidate the cache so the fresh articles.md is re-read this run.
            self.state['articles_cache'] = []
            self._save_state()
            # ASCII-only output: this safety method must never crash on a console
            # codec (e.g. cp1252) that cannot encode emoji.
            print(f"[docx-sync] Regenerated articles.md from updated articles.docx "
                  f"({len(articles)} articles)")
            self.logger.info(
                f"docx auto-sync regenerated articles.md ({len(articles)} articles)"
            )
        except Exception as e:
            # Fail-open: never block posting because the sync failed.
            print(f"[docx-sync] Skipped ({e}); using existing articles.md")
            self.logger.warning(f"docx auto-sync skipped: {e}")

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

        # Defense-in-depth (Option B): pick up a freshly edited articles.docx even
        # if the scheduled .bat sync (Option A) did not run. No-op when up to date.
        self._sync_articles_if_docx_newer()

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
                    print("📄 Step 1: Reading articles from local file...")
                    logger.info("=" * 60)
                    logger.info("ARTICLE READING: Reading from local Markdown file")
                    articles_file = os.getenv('ARTICLES_FILE', 'data/articles.md')
                    logger.info(f"Articles file: {articles_file}")

                    try:
                        articles = await self._read_and_parse_document()
                        logger.info(f"Successfully read {len(articles)} articles from local file")

                        # Log article summary
                        article_numbers = [a.get('number') for a in articles]
                        logger.info(f"Article numbers detected: {article_numbers}")

                        articles_with_content = [a for a in articles if a.get('word_count', 0) > 0]
                        logger.info(f"Articles with content: {len(articles_with_content)}/{len(articles)}")

                        articles_with_urls = [a for a in articles if a.get('has_url', False)]
                        logger.info(f"Articles with URLs: {len(articles_with_urls)}/{len(articles)}")

                    except Exception as e:
                        error_msg = f"Failed to read articles from local file: {str(e)}"
                        logger.error(error_msg)
                        print(f"❌ {error_msg}")
                        raise

                    # Validate URLs before caching
                    print("🔍 Validating article URLs...")
                    logger.info("Starting article validation...")
                    try:
                        self._validate_articles_data(articles)
                        print("✅ All article URLs validated successfully")
                        logger.info("✅ Article URL validation passed")
                    except ValueError as e:
                        error_msg = f"Article validation failed: {str(e)}"
                        print(f"❌ {error_msg}")
                        logger.error(f"❌ {error_msg}")
                        raise

                    self.state["articles_cache"] = articles
                    self._save_state()
                    print(f"✓ Found {len(articles)} articles")
                    logger.info(f"✅ Cached {len(articles)} articles to workflow state")
                    logger.info("=" * 60)
                else:
                    articles = self.state["articles_cache"]
                    print(f"✓ Using cached articles ({len(articles)} total)")
                    logger.info("=" * 60)
                    logger.info("ARTICLE READING: Using cached articles")
                    logger.info(f"Cached article count: {len(articles)}")

                    # Log cache details
                    article_numbers = [a.get('number') for a in articles]
                    logger.info(f"Cached article numbers: {article_numbers}")

                    articles_with_content = [a for a in articles if a.get('word_count', 0) > 0]
                    logger.info(f"Cached articles with content: {len(articles_with_content)}/{len(articles)}")

                    # Validate cached articles
                    try:
                        self._validate_articles_data(articles)
                        logger.info("✅ Cached article validation passed")
                    except ValueError as e:
                        error_msg = f"Cached article validation failed: {str(e)}"
                        logger.error(f"⚠️ {error_msg}")
                        print(f"⚠️ Warning: {error_msg}")
                        # Don't raise here as we want to continue with cached data

                    logger.info("=" * 60)

                # Get processable articles (with content and URLs)
                processable_articles = self._get_processable_articles(articles)
                if not processable_articles:
                    raise ValueError("No processable articles found (articles with content and URLs)")

                print()

                # Step 2: Get current article to post
                current_article_num = self.state["current_article"]
                current_variation = self.state["current_variation"]

                print(f"📝 Step 2: Processing Article #{current_article_num}, Variation {current_variation}")
                logger.info(f"Processing Article #{current_article_num}, Variation {current_variation}")

                article = next((a for a in processable_articles if a["number"] == current_article_num), None)
                if not article:
                    # Try to find the article in all articles and provide helpful error
                    article_in_all = next((a for a in articles if a["number"] == current_article_num), None)
                    if article_in_all:
                        if not article_in_all.get('has_url', False):
                            raise ValueError(f"Article #{current_article_num} found but has no URL (incomplete article)")
                        elif article_in_all.get('word_count', 0) == 0:
                            raise ValueError(f"Article #{current_article_num} found but has no content")
                    raise ValueError(f"Article #{current_article_num} not found in processable articles")
                
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
                logger.info(
                    "Composed tweet content",
                    data={
                        "article_number": tweet['article_number'],
                        "variation_number": tweet['variation_number'],
                        "character_count": tweet['character_count'],
                        "content": tweet['content'],
                    }
                )
                self._append_tweet_audit('composed', tweet)
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
                        logger.info(
                            "Posted tweet content",
                            data={
                                "tweet_id": result['tweet_id'],
                                "article_number": tweet['article_number'],
                                "variation_number": tweet['variation_number'],
                                "content": tweet['content'],
                            }
                        )
                        self._append_tweet_audit('posted', tweet, tweet_id=result['tweet_id'])
                        
                        post_result = {
                            'success': True,
                            'tweet_id': result['tweet_id'],
                            'url': f"https://twitter.com/user/status/{result['tweet_id']}",
                            'posted_at': result['posted_at']
                        }
                        
                        # Update workflow state
                        self.state["last_posted"] = datetime.now().isoformat()
                        self.state["total_posts"] += 1
                        self._update_state_after_post(processable_articles)
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
        """Read and parse the newsletter document from local file."""
        from parsers.article_parser import ArticleParser

        # Read from local Markdown file
        articles_file = os.getenv('ARTICLES_FILE', 'data/articles.md')
        parser = ArticleParser(articles_file)
        articles = parser.parse()

        # Convert to dict format
        return [
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

    def _update_state_after_post(self, articles: List[Dict[str, Any]]):
        """Update workflow state after posting a tweet.

        Uses _get_processable_articles to determine the canonical article
        ordering, ensuring duplicate-URL filtering is applied consistently
        regardless of what the caller passes.
        """
        current_article = self.state["current_article"]
        current_variation = self.state["current_variation"]

        # Delegate to the single source of truth for processable articles
        processable = self._get_processable_articles(articles)
        article_numbers = [a['number'] for a in processable]

        # Move to next variation
        if current_variation < 4:
            self.state["current_variation"] = current_variation + 1
        else:
            # Move to next article
            self.state["current_variation"] = 1

            # Find current article index in the list of articles with content
            try:
                current_index = article_numbers.index(current_article)
                if current_index < len(article_numbers) - 1:
                    # Move to next article with content
                    self.state["current_article"] = article_numbers[current_index + 1]
                else:
                    # Cycle back to first article with content
                    self.state["current_article"] = article_numbers[0]
            except ValueError:
                # Current article not found, start with first article with content
                self.state["current_article"] = article_numbers[0] if article_numbers else 1

        self._save_state()

    def _get_processable_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get articles that can be processed (have content and URLs).
        Filters out duplicate URLs, keeping only the first occurrence.

        Args:
            articles: List of all articles from Google Drive

        Returns:
            List of articles with content and URLs, sorted by article number, with duplicates removed
        """
        processable = [
            a for a in articles
            if a.get('word_count', 0) > 0 and a.get('has_url', False) and a.get('url', '').strip()
        ]

        # Sort by article number to ensure consistent ordering
        processable.sort(key=lambda x: x.get('number', 0))

        # Remove duplicate URLs, keeping the first occurrence (lowest article number)
        seen_urls = set()
        unique_processable = []
        for article in processable:
            url = article.get('url', '').strip()
            if url not in seen_urls:
                seen_urls.add(url)
                unique_processable.append(article)
            else:
                self.logger.info(f"Skipping Article #{article['number']} due to duplicate URL: {url}")

        self.logger.info(f"Found {len(unique_processable)} unique processable articles out of {len(articles)} total")
        for article in unique_processable:
            self.logger.info(f"  - Article #{article['number']}: {article.get('title', 'Untitled')[:50]}...")

        return unique_processable

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

        # Defense-in-depth (Option B): pick up a freshly edited articles.docx even
        # if the scheduled .bat sync (Option A) did not run. No-op when up to date.
        self._sync_articles_if_docx_newer()

        # Initialize MCP App and agents
        async with self.mcp_app.run() as mcp_agent_app:
            logger = mcp_agent_app.logger
            logger.info(f"Generating {weeks}-week pipeline preview")

            # Initialize agents
            await self.initialize_agents()

            # Load articles
            if not self.state.get("articles_cache"):
                all_articles = await self._read_and_parse_document()
                self.state["articles_cache"] = all_articles
                self._save_state()
            else:
                all_articles = self.state["articles_cache"]

            # Get processable articles
            articles = self._get_processable_articles(all_articles)

            # Get posting schedule
            posting_day = os.getenv('POSTING_DAY', 'Monday')
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
        return days.get(day_name.lower(), 0)  # Default to Monday

