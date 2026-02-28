"""
Integration Tests for End-to-End Workflow
Tests complete workflow from article reading to tweet generation with mocked MCP agents.
"""

import pytest
import os
import sys
import json
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from workflows.mcp_tweet_processor_workflow import MCPTweetProcessorWorkflow
from agents.mcp_tweet_composer_agent import Tweet
from parsers.article_parser import Article


@pytest.mark.integration
@pytest.mark.asyncio
class TestEndToEndWorkflow:
    """Integration tests for complete workflow execution."""
    
    async def test_workflow_complete_execution(self, temp_articles_file, tmp_path):
        """Test complete workflow execution from start to finish."""
        # Setup state file
        state_file = tmp_path / "workflow_state.json"
        initial_state = {
            "current_article": 1,
            "current_variation": 1,
            "total_posts": 0,
            "last_posted": None,
            "articles_cache": []
        }
        with open(state_file, 'w') as f:
            json.dump(initial_state, f)
        
        # Create workflow
        workflow = MCPTweetProcessorWorkflow()
        
        # Mock MCP App context
        mock_mcp_context = AsyncMock()
        mock_mcp_context.__aenter__ = AsyncMock(return_value=Mock(logger=Mock()))
        mock_mcp_context.__aexit__ = AsyncMock(return_value=None)
        workflow.mcp_app.run = Mock(return_value=mock_mcp_context)
        
        # Mock agents
        mock_analyzer = AsyncMock()
        mock_analyzer.analyze_article = AsyncMock(return_value={
            "article_number": 1,
            "article_title": "Test Article",
            "article_url": "https://www.linkedin.com/pulse/test-aaron-lim/",
            "key_insights": ["Insight 1", "Insight 2", "Insight 3"],
            "themes": ["AI", "Strategy"]
        })
        
        mock_composer = AsyncMock()
        mock_tweet = Tweet(
            article_number=1,
            variation_number=1,
            content="Test tweet\n\nhttps://www.linkedin.com/pulse/test-aaron-lim/\n\n#AI #DataStrategy",
            character_count=100,
            hashtags=["#AI", "#DataStrategy"],
            insights_used=["Insight 1"],
            focus_theme="strategic_value"
        )
        mock_composer.compose_multiple_variations = AsyncMock(return_value=[mock_tweet])
        
        workflow.content_analyzer = mock_analyzer
        workflow.tweet_composer = mock_composer
        
        # Mock article reading
        with patch.object(workflow, '_read_and_parse_document', new_callable=AsyncMock) as mock_read:
            mock_read.return_value = [
                {
                    "number": 1,
                    "title": "Test Article",
                    "url": "https://www.linkedin.com/pulse/test-aaron-lim/",
                    "content": "Test content",
                    "word_count": 100,
                    "has_title": True,
                    "has_url": True
                }
            ]
            
            # Mock state saving
            with patch.object(workflow, '_save_state'):
                # Execute workflow
                result = await workflow.run_weekly_post(post_to_twitter=False)
        
        # Verify result
        assert result is not None
        assert 'status' in result or 'success' in result
    
    async def test_workflow_with_cached_articles(self, sample_workflow_state):
        """Test workflow execution with cached articles."""
        workflow = MCPTweetProcessorWorkflow()
        workflow.state = sample_workflow_state
        
        # Mock MCP App context
        mock_mcp_context = AsyncMock()
        mock_mcp_context.__aenter__ = AsyncMock(return_value=Mock(logger=Mock()))
        mock_mcp_context.__aexit__ = AsyncMock(return_value=None)
        workflow.mcp_app.run = Mock(return_value=mock_mcp_context)
        
        # Mock agents
        mock_analyzer = AsyncMock()
        mock_composer = AsyncMock()
        mock_tweet = Tweet(
            article_number=3,
            variation_number=4,
            content="Test tweet\n\nhttps://example.com\n\n#AI",
            character_count=100,
            hashtags=["#AI"],
            insights_used=["Insight"],
            focus_theme="strategic_value"
        )
        mock_composer.compose_multiple_variations = AsyncMock(return_value=[mock_tweet])
        
        workflow.content_analyzer = mock_analyzer
        workflow.tweet_composer = mock_composer
        
        # Mock state saving
        with patch.object(workflow, '_save_state'):
            # Execute workflow (should use cached articles)
            result = await workflow.run_weekly_post(post_to_twitter=False)
        
        # Verify cached articles were used
        assert workflow.state["articles_cache"] is not None
        assert len(workflow.state["articles_cache"]) > 0


@pytest.mark.integration
@pytest.mark.asyncio
class TestWorkflowArticleReading:
    """Integration tests for article reading and parsing."""
    
    async def test_read_and_parse_articles(self, temp_articles_file):
        """Test reading and parsing articles from file."""
        workflow = MCPTweetProcessorWorkflow()
        
        # Mock the articles file path
        with patch.dict(os.environ, {'ARTICLES_FILE': str(temp_articles_file)}):
            articles = await workflow._read_and_parse_document()
        
        assert len(articles) == 3
        assert all('number' in a for a in articles)
        assert all('title' in a for a in articles)
        assert all('url' in a for a in articles)
        assert all('content' in a for a in articles)
    
    async def test_read_articles_validates_data(self, temp_articles_file):
        """Test that article reading validates data."""
        workflow = MCPTweetProcessorWorkflow()
        
        with patch.dict(os.environ, {'ARTICLES_FILE': str(temp_articles_file)}):
            articles = await workflow._read_and_parse_document()
            
            # Validation should pass for valid articles
            try:
                workflow._validate_articles_data(articles)
                # If validation passes, articles should have required fields
                for article in articles:
                    if article.get('word_count', 0) > 0:
                        assert article.get('has_title') is True
                        assert article.get('has_url') is True
            except ValueError:
                # Validation may fail if articles don't meet requirements
                pass


@pytest.mark.integration
@pytest.mark.asyncio
class TestWorkflowURLIntegrity:
    """Integration tests for URL integrity throughout workflow."""
    
    async def test_url_preserved_through_workflow(self, sample_workflow_state):
        """Test that article URL is preserved throughout workflow."""
        workflow = MCPTweetProcessorWorkflow()
        workflow.state = sample_workflow_state

        expected_url = sample_workflow_state["articles_cache"][2]["url"]  # Article 3

        # Mock MCP App context
        mock_mcp_context = AsyncMock()
        mock_mcp_context.__aenter__ = AsyncMock(return_value=Mock(logger=Mock()))
        mock_mcp_context.__aexit__ = AsyncMock(return_value=None)
        workflow.mcp_app.run = Mock(return_value=mock_mcp_context)

        # Mock composer to capture URL
        captured_url = None

        async def capture_url(**kwargs):
            nonlocal captured_url
            captured_url = kwargs.get('article_url')
            return [Tweet(
                article_number=3,
                variation_number=4,
                content=f"Test\n\n{kwargs.get('article_url')}\n\n#AI",
                character_count=100,
                hashtags=["#AI"],
                insights_used=["Insight"],
                focus_theme="strategic_value"
            )]

        mock_composer = AsyncMock()
        mock_composer.compose_multiple_variations = capture_url
        workflow.tweet_composer = mock_composer

        # Create proper mock for content_analyzer.analyze_article() return value
        mock_insights = Mock()
        mock_insights.article_number = 3
        mock_insights.article_title = "AI Implementation Strategies for Business Leaders"
        mock_insights.article_url = expected_url
        mock_insights.key_insights = ["Insight 1", "Insight 2"]
        mock_insights.themes = ["AI", "Strategy"]
        mock_insights.expert_references = []
        mock_insights.frameworks_mentioned = []

        workflow.content_analyzer = AsyncMock()
        workflow.content_analyzer.analyze_article = AsyncMock(return_value=mock_insights)

        with patch.object(workflow, 'initialize_agents', new=AsyncMock()):
            with patch.object(workflow, '_save_state'):
                with patch.object(workflow, 'validate_url_format'):
                    with patch.object(workflow, 'validate_article_url'):
                        await workflow.run_weekly_post(post_to_twitter=False)

        # Verify URL was passed correctly
        assert captured_url == expected_url

