"""
Integration Tests for Tweet Processor Workflow
Tests the full tweet generation workflow and validates URL integrity end-to-end.
"""

import pytest
import json
import os
import sys
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, List, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from workflows.mcp_tweet_processor_workflow import MCPTweetProcessorWorkflow


class TestWorkflowIntegration:
    """Integration tests for the complete tweet generation workflow."""
    
    @pytest.fixture
    def mock_workflow(self):
        """Create a mock workflow instance for testing."""
        workflow = MCPTweetProcessorWorkflow()
        
        # Mock the MCP components
        workflow.content_analyzer = Mock()
        workflow.tweet_composer = Mock()
        
        return workflow
    
    @pytest.fixture
    def sample_articles(self):
        """Sample article data for testing with valid LinkedIn URL patterns."""
        return [
            {
                'number': 1,
                'title': 'Creating Business Value with AI (Part 2) - What I Learned from Cornell (Republished Version)',
                'url': 'https://www.linkedin.com/pulse/creating-business-value-ai-part-1-what-i-learned-from-lim-ywfmc/',
                'content': 'Sample content for article 1...',
                'word_count': 191,
                'has_title': True,
                'has_url': True
            },
            {
                'number': 2,
                'title': 'Leveraging Data for AI Solutions (Part 3) - Data Quality and Preparation',
                'url': 'https://www.linkedin.com/pulse/leveraging-data-ai-solutions-part-3-lim-abc123/',
                'content': 'Sample content for article 2...',
                'word_count': 112,
                'has_title': True,
                'has_url': True
            },
            {
                'number': 3,
                'title': 'AI Implementation Strategies for Business Leaders',
                'url': 'https://www.linkedin.com/pulse/ai-implementation-strategies-business-leaders-lim-def456/',
                'content': 'Sample content for article 3...',
                'word_count': 97,
                'has_title': True,
                'has_url': True
            }
        ]
    
    @pytest.mark.asyncio
    async def test_full_workflow_url_integrity(self, mock_workflow, sample_articles):
        """Test that the full workflow maintains URL integrity from article to tweet."""
        
        # Mock the article loading
        mock_workflow._load_articles = AsyncMock(return_value=sample_articles)
        
        # Mock analysis results
        mock_analysis = {
            'article_number': 3,
            'article_title': 'AI Implementation Strategies for Business Leaders',
            'article_url': 'https://www.linkedin.com/pulse/ai-implementation-strategies-business-leaders-lim-def456/',
            'key_insights': ['Insight 1', 'Insight 2', 'Insight 3'],
            'themes': ['AI', 'Strategy']
        }
        
        # Mock tweet composition result
        mock_tweet = Mock()
        mock_tweet.content = "Test tweet content\n\nhttps://www.linkedin.com/pulse/ai-implementation-strategies-business-leaders-lim-def456/\n\n#AI #Strategy"
        mock_tweet.character_count = 150
        mock_tweet.article_number = 3
        
        mock_workflow.tweet_composer.compose_multiple_variations = AsyncMock(
            return_value=[mock_tweet]
        )
        
        # Set workflow state to process Article #3
        mock_workflow.state = {
            'current_article': 3,
            'current_variation': 1,
            'articles_cache': sample_articles,
            'analysis_3': mock_analysis
        }
        
        # Execute workflow
        result = await mock_workflow.run_weekly_post(post_to_twitter=False)

        # Verify URL integrity - workflow returns 'status' not 'success'
        assert result['status'] == 'success'
        tweet_content = result['tweet']['content']
        expected_url = 'https://www.linkedin.com/pulse/ai-implementation-strategies-business-leaders-lim-def456/'

        assert expected_url in tweet_content, \
            f"Expected URL not found in tweet content.\n" \
            f"Expected: {expected_url}\n" \
            f"Tweet: {tweet_content}"

        # URL integrity verified through the successful result containing the expected URL
    
    @pytest.mark.asyncio
    async def test_workflow_url_validation_for_all_articles(self, mock_workflow, sample_articles):
        """Test URL validation for all articles in the workflow."""
        
        mock_workflow._load_articles = AsyncMock(return_value=sample_articles)
        
        for article in sample_articles:
            article_number = article['number']
            expected_url = article['url']
            
            # Mock analysis for this article
            mock_analysis = {
                'article_number': article_number,
                'article_title': article['title'],
                'article_url': expected_url,
                'key_insights': ['Insight 1', 'Insight 2'],
                'themes': ['AI']
            }
            
            # Mock tweet result
            mock_tweet = Mock()
            mock_tweet.content = f"Test tweet for article {article_number}\n\n{expected_url}\n\n#AI"
            mock_tweet.article_number = article_number
            
            mock_workflow.tweet_composer.compose_multiple_variations = AsyncMock(
                return_value=[mock_tweet]
            )
            
            # Set workflow state
            mock_workflow.state = {
                'current_article': article_number,
                'current_variation': 1,
                'articles_cache': sample_articles,
                f'analysis_{article_number}': mock_analysis
            }
            
            # Execute workflow
            result = await mock_workflow.run_weekly_post(post_to_twitter=False)

            # Verify URL integrity - workflow returns 'status' not 'success'
            assert result['status'] == 'success'
            tweet_content = result['tweet']['content']

            assert expected_url in tweet_content, \
                f"Article #{article_number}: Expected URL not found in tweet.\n" \
                f"Expected: {expected_url}\n" \
                f"Tweet: {tweet_content}"

    def test_url_extraction_from_workflow_state(self, isolated_workflow_state_data):
        """Test URL extraction from workflow state data."""
        articles_cache = isolated_workflow_state_data.get('articles_cache', [])

        # Test URL extraction for each article
        for article in articles_cache:
            article_number = article['number']
            article_url = article['url']

            # Verify URL is not empty (except Article #5 which can have empty URL)
            if article_number != 5:
                assert article_url and article_url.strip(), \
                    f"Article #{article_number} has empty URL"

            # Verify URL format (if URL exists)
            if article_url and article_url.strip():
                assert article_url.startswith('https://'), \
                    f"Article #{article_number} URL doesn't start with https://"

                # Verify LinkedIn domain
                assert 'linkedin.com/pulse/' in article_url, \
                    f"Article #{article_number} URL is not a LinkedIn pulse URL"
    
    @pytest.mark.asyncio
    async def test_error_handling_for_missing_url(self, mock_workflow):
        """Test error handling when article URL is missing or invalid."""
        
        # Create article with missing URL
        invalid_article = {
            'number': 1,
            'title': 'Test Article',
            'url': '',  # Empty URL
            'content': 'Test content',
            'has_url': False
        }
        
        mock_workflow._load_articles = AsyncMock(return_value=[invalid_article])
        mock_workflow.state = {
            'current_article': 1,
            'current_variation': 1,
            'articles_cache': [invalid_article]
        }

        # The workflow catches exceptions and returns error status
        result = await mock_workflow.run_weekly_post(post_to_twitter=False)
        assert result['status'] == 'error', "Expected error status for missing URL"
        assert 'No processable articles found' in result.get('error', ''), \
            f"Expected 'No processable articles found' in error message, got: {result.get('error', '')}"
    
    @pytest.mark.asyncio
    async def test_url_mismatch_detection(self, mock_workflow, sample_articles):
        """Test detection of URL mismatches between article cache and analysis cache."""
        
        mock_workflow._load_articles = AsyncMock(return_value=sample_articles)
        
        # Create mismatched analysis (Article 3 with Article 2's URL)
        mismatched_analysis = {
            'article_number': 3,
            'article_title': 'AI Implementation Strategies for Business Leaders',
            'article_url': 'https://www.linkedin.com/pulse/leveraging-data-ai-solutions-part-3-lim-abc123/',  # Wrong URL!
            'key_insights': ['Insight 1'],
            'themes': ['AI']
        }
        
        mock_workflow.state = {
            'current_article': 3,
            'current_variation': 1,
            'articles_cache': sample_articles,
            'analysis_3': mismatched_analysis
        }

        # The workflow catches exceptions and returns error status
        result = await mock_workflow.run_weekly_post(post_to_twitter=False)
        assert result['status'] == 'error', "Expected error status for URL mismatch"
        assert 'URL mismatch detected' in result.get('error', ''), \
            f"Expected 'URL mismatch detected' in error message, got: {result.get('error', '')}"


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
