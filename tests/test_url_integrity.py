"""
URL Integrity Tests for Tweet Processor
Tests to ensure each article number correctly maps to its corresponding URL.
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
from agents.mcp_tweet_composer_agent import MCPTweetComposerAgent


class TestURLIntegrity:
    """Test suite for URL integrity validation."""

    @pytest.fixture
    def expected_url_mappings(self):
        """Expected URL mappings for each article."""
        return {
            1: "https://www.linkedin.com/pulse/creating-business-value-ai-part-1-what-i-learned-from-lim-ywfmc/",
            2: "https://www.linkedin.com/pulse/leveraging-data-ai-solutions-part-3-aaron-lim/",
            3: "https://www.linkedin.com/pulse/ai-implementation-strategies-business-leaders-aaron-lim/",
            4: "https://www.linkedin.com/pulse/ethical-ai-responsible-innovation-aaron-lim/",
            5: "https://www.linkedin.com/pulse/measuring-ai-success-metrics-kpis-aaron-lim/"
        }

    def test_workflow_state_url_mappings(self, isolated_workflow_state_data, expected_url_mappings):
        """Test that workflow state contains correct URL mappings for all articles."""
        articles_cache = isolated_workflow_state_data.get('articles_cache', [])

        # Verify we have all 5 articles
        assert len(articles_cache) == 5, f"Expected 5 articles, found {len(articles_cache)}"

        # Test each article has correct URL
        for article in articles_cache:
            article_number = article['number']
            article_url = article['url']
            expected_url = expected_url_mappings[article_number]
            
            assert article_url == expected_url, \
                f"Article #{article_number} has incorrect URL.\n" \
                f"Expected: {expected_url}\n" \
                f"Actual: {article_url}"
    
    def test_analysis_cache_url_mappings(self, isolated_workflow_state_data, expected_url_mappings):
        """Test that analysis cache contains correct URL mappings for all articles."""
        for article_number in range(1, 6):
            analysis_key = f"analysis_{article_number}"

            # Check if analysis exists
            assert analysis_key in isolated_workflow_state_data, \
                f"Analysis cache missing for Article #{article_number}"

            analysis = isolated_workflow_state_data[analysis_key]
            analysis_url = analysis['article_url']
            expected_url = expected_url_mappings[article_number]

            assert analysis_url == expected_url, \
                f"Analysis cache for Article #{article_number} has incorrect URL.\n" \
                f"Expected: {expected_url}\n" \
                f"Actual: {analysis_url}"

    def test_url_uniqueness(self, isolated_workflow_state_data):
        """Test that all articles have unique URLs (no duplicates)."""
        articles_cache = isolated_workflow_state_data.get('articles_cache', [])
        urls = [article['url'] for article in articles_cache]

        # Check for duplicates
        unique_urls = set(urls)
        assert len(urls) == len(unique_urls), \
            f"Duplicate URLs found. URLs: {urls}"

        # Verify each URL is different
        assert len(unique_urls) == 5, \
            f"Expected 5 unique URLs, found {len(unique_urls)}"

    def test_url_format_validation(self, isolated_workflow_state_data):
        """Test that all URLs follow the expected LinkedIn format."""
        articles_cache = isolated_workflow_state_data.get('articles_cache', [])
        
        for article in articles_cache:
            url = article['url']
            article_number = article['number']
            
            # Check URL format
            assert url.startswith('https://www.linkedin.com/pulse/'), \
                f"Article #{article_number} URL doesn't start with LinkedIn pulse URL: {url}"
            
            # Check for valid ending patterns (different articles have different patterns)
            valid_endings = ['-aaron-lim/', '-lim-ywfmc/']
            assert any(url.endswith(ending) for ending in valid_endings), \
                f"Article #{article_number} URL doesn't end with expected pattern: {url}"
            
            # Check URL is not empty or None
            assert url and url.strip(), \
                f"Article #{article_number} has empty or None URL"
    
    @pytest.mark.asyncio
    async def test_tweet_composer_url_usage(self, expected_url_mappings):
        """Test that tweet composer correctly uses the provided article URL."""
        # Mock the MCP Agent components
        mock_agent = Mock()
        mock_llm = AsyncMock()
        mock_llm.generate_str.return_value = "Test tweet content about AI implementation"
        
        composer = MCPTweetComposerAgent(agent=mock_agent)
        composer.llm = mock_llm
        
        # Test each article URL
        for article_number, expected_url in expected_url_mappings.items():
            tweet_content, insights_used = await composer.compose_tweet(
                article_title=f"Test Article {article_number}",
                article_url=expected_url,
                insights=["Test insight 1", "Test insight 2"],
                themes=["AI", "Strategy"],
                variation_number=1
            )
            
            # Verify the URL appears in the tweet content
            assert expected_url in tweet_content, \
                f"Article #{article_number} URL not found in tweet content.\n" \
                f"Expected URL: {expected_url}\n" \
                f"Tweet content: {tweet_content}"
    
    def test_article_number_url_consistency(self, isolated_workflow_state_data):
        """Test that article numbers are consistent between cache and analysis."""
        articles_cache = isolated_workflow_state_data.get('articles_cache', [])

        for article in articles_cache:
            article_number = article['number']
            article_url = article['url']

            # Check corresponding analysis
            analysis_key = f"analysis_{article_number}"
            if analysis_key in isolated_workflow_state_data:
                analysis = isolated_workflow_state_data[analysis_key]
                analysis_number = analysis['article_number']
                analysis_url = analysis['article_url']

                # Verify numbers match
                assert article_number == analysis_number, \
                    f"Article number mismatch: cache={article_number}, analysis={analysis_number}"

                # Verify URLs match
                assert article_url == analysis_url, \
                    f"URL mismatch for Article #{article_number}:\n" \
                    f"Cache URL: {article_url}\n" \
                    f"Analysis URL: {analysis_url}"


class TestURLValidationLogic:
    """Test suite for URL validation logic."""
    
    def test_url_to_article_mapping_validation(self, expected_url_mappings=None):
        """Test URL to article number mapping validation."""
        if expected_url_mappings is None:
            expected_url_mappings = {
                1: "https://www.linkedin.com/pulse/creating-business-value-ai-part-1-what-i-learned-from-lim-ywfmc/",
                2: "https://www.linkedin.com/pulse/leveraging-data-ai-solutions-part-3-aaron-lim/",
                3: "https://www.linkedin.com/pulse/ai-implementation-strategies-business-leaders-aaron-lim/",
                4: "https://www.linkedin.com/pulse/ethical-ai-responsible-innovation-aaron-lim/",
                5: "https://www.linkedin.com/pulse/measuring-ai-success-metrics-kpis-aaron-lim/"
            }
        
        # Test correct mappings
        for article_number, expected_url in expected_url_mappings.items():
            # This would use the validation function we'll implement
            assert self._validate_url_for_article(article_number, expected_url) == True
        
        # Test incorrect mappings (should fail)
        with pytest.raises(AssertionError):
            # Article 1 with Article 2's URL should fail
            self._validate_url_for_article(1, expected_url_mappings[2])
    
    def _validate_url_for_article(self, article_number: int, url: str) -> bool:
        """Helper method to validate URL for article number."""
        expected_mappings = {
            1: "creating-business-value-ai-part-1-what-i-learned-from-lim",
            2: "leveraging-data-ai-solutions-part-3-aaron-lim",
            3: "ai-implementation-strategies-business-leaders-aaron-lim",
            4: "ethical-ai-responsible-innovation-aaron-lim",
            5: "measuring-ai-success-metrics-kpis-aaron-lim"
        }
        
        expected_slug = expected_mappings.get(article_number)
        if not expected_slug:
            raise ValueError(f"Unknown article number: {article_number}")
        
        # Check if URL contains the expected slug
        if expected_slug not in url:
            raise AssertionError(
                f"URL validation failed for Article #{article_number}.\n"
                f"Expected URL to contain: {expected_slug}\n"
                f"Actual URL: {url}"
            )
        
        return True


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
