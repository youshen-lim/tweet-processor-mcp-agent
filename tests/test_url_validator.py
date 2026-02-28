"""
Unit Tests for URL Validator
Tests URL format validation, uniqueness checks, and article-URL mapping.
"""

import pytest
import os
import sys
import logging

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.url_validator import URLValidator


@pytest.mark.unit
class TestURLValidatorInitialization:
    """Test suite for URLValidator initialization."""
    
    def test_validator_creation_without_logger(self):
        """Test creating validator without logger."""
        validator = URLValidator()
        assert validator.logger is not None
    
    def test_validator_creation_with_logger(self):
        """Test creating validator with custom logger."""
        custom_logger = logging.getLogger("test_logger")
        validator = URLValidator(logger=custom_logger)
        assert validator.logger == custom_logger


@pytest.mark.unit
class TestURLFormatValidation:
    """Test suite for URL format validation."""
    
    def test_validate_valid_linkedin_url(self):
        """Test validation of valid LinkedIn pulse URL."""
        validator = URLValidator()
        url = "https://www.linkedin.com/pulse/creating-business-value-ai-part-1-what-i-learned-from-lim-ywfmc/"
        
        result = validator.validate_url_format(url, article_number=1)
        assert result is True
    
    def test_validate_url_without_https(self):
        """Test validation fails for URL without https."""
        validator = URLValidator()
        url = "http://www.linkedin.com/pulse/test-aaron-lim/"
        
        with pytest.raises(ValueError) as exc_info:
            validator.validate_url_format(url, article_number=1)
        
        assert "must start with https://" in str(exc_info.value)
    
    def test_validate_url_not_linkedin(self):
        """Test validation fails for non-LinkedIn URL."""
        validator = URLValidator()
        url = "https://www.example.com/article"
        
        with pytest.raises(ValueError) as exc_info:
            validator.validate_url_format(url, article_number=1)
        
        assert "must be a LinkedIn pulse URL" in str(exc_info.value)
    
    def test_validate_url_missing_pulse(self):
        """Test validation fails for LinkedIn URL without pulse."""
        validator = URLValidator()
        url = "https://www.linkedin.com/in/aaron-lim/"
        
        with pytest.raises(ValueError) as exc_info:
            validator.validate_url_format(url, article_number=1)
        
        assert "must be a LinkedIn pulse URL" in str(exc_info.value)
    
    def test_validate_url_invalid_ending(self):
        """Test validation fails for URL with invalid ending pattern."""
        validator = URLValidator()
        url = "https://www.linkedin.com/pulse/test-article"
        
        with pytest.raises(ValueError) as exc_info:
            validator.validate_url_format(url, article_number=1)
        
        assert "must end with LinkedIn author pattern" in str(exc_info.value)
    
    def test_validate_empty_url(self):
        """Test validation fails for empty URL."""
        validator = URLValidator()
        
        with pytest.raises(ValueError) as exc_info:
            validator.validate_url_format("", article_number=1)
        
        assert "has empty URL" in str(exc_info.value)
    
    def test_validate_whitespace_url(self):
        """Test validation fails for whitespace-only URL."""
        validator = URLValidator()
        
        with pytest.raises(ValueError) as exc_info:
            validator.validate_url_format("   ", article_number=1)
        
        assert "has empty URL" in str(exc_info.value)
    
    def test_validate_url_with_different_author_patterns(self):
        """Test validation accepts different valid author patterns."""
        validator = URLValidator()
        
        # Pattern 1: -lim-ywfmc/
        url1 = "https://www.linkedin.com/pulse/test-article-lim-ywfmc/"
        assert validator.validate_url_format(url1) is True
        
        # Pattern 2: -lim-abc123/
        url2 = "https://www.linkedin.com/pulse/test-article-lim-abc123/"
        assert validator.validate_url_format(url2) is True


@pytest.mark.unit
class TestArticleURLValidation:
    """Test suite for article-specific URL validation."""
    
    def test_validate_article_url_valid(self):
        """Test validation of valid article URL."""
        validator = URLValidator()
        url = "https://www.linkedin.com/pulse/creating-business-value-ai-part-1-what-i-learned-from-lim-ywfmc/"
        
        result = validator.validate_article_url(1, url)
        assert result is True
    
    def test_validate_article_url_invalid_number(self):
        """Test validation fails for invalid article number."""
        validator = URLValidator()
        url = "https://www.linkedin.com/pulse/test-aaron-lim/"
        
        with pytest.raises(ValueError) as exc_info:
            validator.validate_article_url(0, url)
        
        assert "Invalid article number" in str(exc_info.value)
    
    def test_validate_article_url_negative_number(self):
        """Test validation fails for negative article number."""
        validator = URLValidator()
        url = "https://www.linkedin.com/pulse/test-aaron-lim/"
        
        with pytest.raises(ValueError) as exc_info:
            validator.validate_article_url(-1, url)
        
        assert "Invalid article number" in str(exc_info.value)
    
    def test_validate_article_url_empty_for_article_5(self):
        """Test validation allows empty URL for Article #5 (special case)."""
        validator = URLValidator()
        
        # Article #5 is allowed to have no URL
        result = validator.validate_article_url(5, "")
        assert result is True
    
    def test_validate_article_url_empty_for_other_articles(self):
        """Test validation fails for empty URL on non-Article #5."""
        validator = URLValidator()

        with pytest.raises(ValueError) as exc_info:
            validator.validate_article_url(1, "")

        assert "has empty or None URL" in str(exc_info.value)


@pytest.mark.unit
class TestURLUniquenessValidation:
    """Test suite for URL uniqueness validation."""

    def test_validate_unique_urls(self):
        """Test validation passes for unique URLs."""
        validator = URLValidator()
        articles = [
            {"number": 1, "url": "https://www.linkedin.com/pulse/article-1-lim-abc/"},
            {"number": 2, "url": "https://www.linkedin.com/pulse/article-2-lim-def/"},
            {"number": 3, "url": "https://www.linkedin.com/pulse/article-3-lim-ghi/"}
        ]

        result = validator.validate_url_uniqueness(articles)
        assert result is True

    def test_validate_duplicate_urls(self):
        """Test validation fails for duplicate URLs."""
        validator = URLValidator()
        articles = [
            {"number": 1, "url": "https://www.linkedin.com/pulse/article-1-lim-abc/"},
            {"number": 2, "url": "https://www.linkedin.com/pulse/article-1-lim-abc/"},  # Duplicate
            {"number": 3, "url": "https://www.linkedin.com/pulse/article-3-lim-ghi/"}
        ]

        with pytest.raises(ValueError) as exc_info:
            validator.validate_url_uniqueness(articles)

        assert "Duplicate URLs found" in str(exc_info.value)

    def test_validate_uniqueness_ignores_empty_urls(self):
        """Test uniqueness validation ignores empty URLs."""
        validator = URLValidator()
        articles = [
            {"number": 1, "url": "https://www.linkedin.com/pulse/article-1-lim-abc/"},
            {"number": 2, "url": ""},  # Empty URL
            {"number": 3, "url": "https://www.linkedin.com/pulse/article-3-lim-ghi/"}
        ]

        # Should not raise error for empty URLs
        result = validator.validate_url_uniqueness(articles)
        assert result is True


@pytest.mark.unit
class TestArticlesDataValidation:
    """Test suite for comprehensive articles data validation."""

    def test_validate_valid_articles_data(self):
        """Test validation of valid articles data."""
        validator = URLValidator()
        articles = [
            {
                "number": 1,
                "title": "Article 1",
                "url": "https://www.linkedin.com/pulse/article-1-lim-abc/",
                "content": "Content 1",
                "word_count": 100
            },
            {
                "number": 2,
                "title": "Article 2",
                "url": "https://www.linkedin.com/pulse/article-2-lim-def/",
                "content": "Content 2",
                "word_count": 150
            },
            {
                "number": 3,
                "title": "Article 3",
                "url": "https://www.linkedin.com/pulse/article-3-lim-ghi/",
                "content": "Content 3",
                "word_count": 200
            },
            {
                "number": 4,
                "title": "Article 4",
                "url": "https://www.linkedin.com/pulse/article-4-lim-jkl/",
                "content": "Content 4",
                "word_count": 175
            },
            {
                "number": 5,
                "title": "Article 5",
                "url": "",  # Article 5 can have empty URL
                "content": "Content 5",
                "word_count": 0
            }
        ]

        result = validator.validate_articles_data(articles, expected_count=5)
        assert result['total_articles'] == 5
        assert result['valid_articles'] == 5  # All 5 should be valid (Article 5 empty URL is allowed)

    def test_validate_empty_articles_list(self):
        """Test validation fails for empty articles list."""
        validator = URLValidator()

        with pytest.raises(ValueError) as exc_info:
            validator.validate_articles_data([])

        assert "No articles found" in str(exc_info.value)

    def test_validate_wrong_article_count(self):
        """Test validation fails for wrong number of articles when expected_count is specified."""
        validator = URLValidator()
        articles = [
            {"number": 1, "title": "Article 1", "url": "https://www.linkedin.com/pulse/article-1-lim-abc/"}
        ]

        # Should fail when expected_count=5 but only 1 article provided
        with pytest.raises(ValueError) as exc_info:
            validator.validate_articles_data(articles, expected_count=5)

        assert "Expected 5 articles, found 1" in str(exc_info.value)

    def test_validate_dynamic_article_count(self):
        """Test validation accepts any number of articles when expected_count is not specified."""
        validator = URLValidator()

        # Test with 1 article
        articles_1 = [
            {"number": 1, "title": "Article 1", "url": "https://www.linkedin.com/pulse/article-1-lim-abc/"}
        ]
        result = validator.validate_articles_data(articles_1)
        assert result['total_articles'] == 1
        assert result['valid_articles'] == 1

        # Test with 3 articles
        articles_3 = [
            {"number": 1, "title": "Article 1", "url": "https://www.linkedin.com/pulse/article-1-lim-abc/"},
            {"number": 2, "title": "Article 2", "url": "https://www.linkedin.com/pulse/article-2-lim-def/"},
            {"number": 3, "title": "Article 3", "url": "https://www.linkedin.com/pulse/article-3-lim-ghi/"}
        ]
        result = validator.validate_articles_data(articles_3)
        assert result['total_articles'] == 3
        assert result['valid_articles'] == 3

        # Test with 10 articles
        articles_10 = [
            {"number": i, "title": f"Article {i}", "url": f"https://www.linkedin.com/pulse/article-{i}-lim-{chr(97+i)}/"}
            for i in range(1, 11)
        ]
        result = validator.validate_articles_data(articles_10)
        assert result['total_articles'] == 10
        assert result['valid_articles'] == 10

    def test_validate_missing_article_number(self):
        """Test validation fails for missing article number."""
        validator = URLValidator()
        articles = [
            {"title": "Article", "url": "https://www.linkedin.com/pulse/article-lim-abc/"},
            {"number": 2, "title": "Article 2", "url": "https://www.linkedin.com/pulse/article-2-lim-def/"},
            {"number": 3, "title": "Article 3", "url": "https://www.linkedin.com/pulse/article-3-lim-ghi/"},
            {"number": 4, "title": "Article 4", "url": "https://www.linkedin.com/pulse/article-4-lim-jkl/"},
            {"number": 5, "title": "Article 5", "url": ""}
        ]

        with pytest.raises(ValueError) as exc_info:
            validator.validate_articles_data(articles)

        assert "missing 'number' field" in str(exc_info.value)

    def test_validate_duplicate_article_numbers(self):
        """Test validation fails for duplicate article numbers."""
        validator = URLValidator()
        articles = [
            {"number": 1, "title": "Article 1", "url": "https://www.linkedin.com/pulse/article-1-lim-abc/"},
            {"number": 1, "title": "Article 1 Duplicate", "url": "https://www.linkedin.com/pulse/article-1b-lim-def/"},
            {"number": 3, "title": "Article 3", "url": "https://www.linkedin.com/pulse/article-3-lim-ghi/"},
            {"number": 4, "title": "Article 4", "url": "https://www.linkedin.com/pulse/article-4-lim-jkl/"},
            {"number": 5, "title": "Article 5", "url": ""}
        ]

        with pytest.raises(ValueError) as exc_info:
            validator.validate_articles_data(articles)

        assert "Duplicate article numbers" in str(exc_info.value)


@pytest.mark.unit
class TestValidationReporting:
    """Test suite for validation reporting functionality."""

    def test_generate_validation_report(self):
        """Test generating validation report."""
        validator = URLValidator()
        articles = [
            {"number": 1, "title": "Article 1", "url": "https://www.linkedin.com/pulse/article-1-lim-abc/"},
            {"number": 2, "title": "Article 2", "url": "invalid-url"}
        ]

        report = validator.generate_validation_report(articles)

        assert "URL VALIDATION REPORT" in report
        assert "Article #1" in report
        assert "Article #2" in report
        assert "✅ VALID" in report or "❌ INVALID" in report

    def test_log_validation_report(self, caplog):
        """Test logging validation report."""
        validator = URLValidator()
        articles = [
            {"number": 1, "title": "Article 1", "url": "https://www.linkedin.com/pulse/article-1-lim-abc/"}
        ]

        with caplog.at_level(logging.INFO):
            validator.log_validation_report(articles)

        # Check that something was logged
        assert len(caplog.records) > 0

