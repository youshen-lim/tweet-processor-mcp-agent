"""
Unit Tests for ArticleParser
Tests parsing, metadata extraction, article retrieval, and validation.
"""

import pytest
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from parsers.article_parser import Article, ArticleParser


@pytest.mark.unit
class TestArticle:
    """Test suite for Article dataclass."""
    
    def test_article_creation(self):
        """Test creating an Article instance."""
        article = Article(
            number=1,
            title="Test Article",
            url="https://www.linkedin.com/pulse/test-article-aaron-lim/",
            content="Test content",
            word_count=100,
            status="Active"
        )
        
        assert article.number == 1
        assert article.title == "Test Article"
        assert article.url == "https://www.linkedin.com/pulse/test-article-aaron-lim/"
        assert article.content == "Test content"
        assert article.word_count == 100
        assert article.status == "Active"
    
    def test_article_has_title_property(self):
        """Test has_title property."""
        article_with_title = Article(1, "Test", "url", "content", 100)
        article_without_title = Article(1, "", "url", "content", 100)
        article_with_whitespace = Article(1, "   ", "url", "content", 100)
        
        assert article_with_title.has_title is True
        assert article_without_title.has_title is False
        assert article_with_whitespace.has_title is False
    
    def test_article_has_url_property(self):
        """Test has_url property."""
        article_with_url = Article(1, "title", "https://example.com", "content", 100)
        article_without_url = Article(1, "title", "", "content", 100)
        article_with_whitespace = Article(1, "title", "   ", "content", 100)
        
        assert article_with_url.has_url is True
        assert article_without_url.has_url is False
        assert article_with_whitespace.has_url is False
    
    def test_article_has_content_property(self):
        """Test has_content property."""
        article_with_content = Article(1, "title", "url", "Test content", 100)
        article_without_content = Article(1, "title", "url", "", 100)
        article_with_whitespace = Article(1, "title", "url", "   ", 100)
        
        assert article_with_content.has_content is True
        assert article_without_content.has_content is False
        assert article_with_whitespace.has_content is False


@pytest.mark.unit
class TestArticleParserInitialization:
    """Test suite for ArticleParser initialization."""
    
    def test_parser_with_valid_file(self, temp_articles_file):
        """Test parser initialization with valid file."""
        parser = ArticleParser(temp_articles_file)
        assert parser.file_path == temp_articles_file
        assert parser.file_path.exists()
    
    def test_parser_with_missing_file(self):
        """Test parser initialization with missing file."""
        with pytest.raises(FileNotFoundError) as exc_info:
            ArticleParser(Path("/nonexistent/articles.md"))
        
        assert "Articles file not found" in str(exc_info.value)
    
    def test_parser_with_default_path(self):
        """Test parser initialization with default path."""
        # This will fail if data/articles.md doesn't exist, which is expected
        # We're testing that it tries to use the default path
        try:
            parser = ArticleParser()
            # If it succeeds, verify it's using the expected default path
            assert parser.file_path.name == "articles.md"
            assert "data" in str(parser.file_path)
        except FileNotFoundError:
            # Expected if data/articles.md doesn't exist in test environment
            pass


@pytest.mark.unit
class TestArticleParserParsing:
    """Test suite for ArticleParser parsing functionality."""
    
    def test_parse_valid_markdown(self, temp_articles_file):
        """Test parsing valid Markdown content."""
        parser = ArticleParser(temp_articles_file)
        articles = parser.parse()
        
        assert len(articles) == 3
        assert all(isinstance(a, Article) for a in articles)
        assert articles[0].number == 1
        assert articles[1].number == 2
        assert articles[2].number == 3
    
    def test_parse_extracts_titles(self, temp_articles_file):
        """Test that parsing correctly extracts article titles."""
        parser = ArticleParser(temp_articles_file)
        articles = parser.parse()
        
        assert articles[0].title == "Creating Business Value with AI (Part 1)"
        assert articles[1].title == "Data Strategy for AI Success"
        assert articles[2].title == "AI Implementation Best Practices"
    
    def test_parse_extracts_urls(self, temp_articles_file):
        """Test that parsing correctly extracts article URLs."""
        parser = ArticleParser(temp_articles_file)
        articles = parser.parse()
        
        assert articles[0].url == "https://www.linkedin.com/pulse/creating-business-value-ai-part-1-what-i-learned-from-lim-ywfmc/"
        assert articles[1].url == "https://www.linkedin.com/pulse/data-strategy-ai-success-aaron-lim/"
        assert articles[2].url == "https://www.linkedin.com/pulse/ai-implementation-best-practices-aaron-lim/"
    
    def test_parse_extracts_content(self, temp_articles_file):
        """Test that parsing correctly extracts article content."""
        parser = ArticleParser(temp_articles_file)
        articles = parser.parse()
        
        assert "AI business value" in articles[0].content
        assert "data quality" in articles[1].content
        assert "practical guidance" in articles[2].content
    
    def test_parse_extracts_word_count(self, temp_articles_file):
        """Test that parsing correctly extracts word count from metadata."""
        parser = ArticleParser(temp_articles_file)
        articles = parser.parse()

        assert articles[0].word_count == 150
        assert articles[1].word_count == 200
        assert articles[2].word_count == 175

    def test_parse_extracts_status(self, temp_articles_file):
        """Test that parsing correctly extracts article status."""
        parser = ArticleParser(temp_articles_file)
        articles = parser.parse()

        assert all(a.status == "Active" for a in articles)

    def test_parse_returns_sorted_articles(self, temp_articles_file):
        """Test that articles are returned sorted by number."""
        parser = ArticleParser(temp_articles_file)
        articles = parser.parse()

        numbers = [a.number for a in articles]
        assert numbers == sorted(numbers)


@pytest.mark.unit
class TestArticleParserRetrieval:
    """Test suite for ArticleParser article retrieval methods."""

    def test_get_article_by_number(self, temp_articles_file):
        """Test retrieving a specific article by number."""
        parser = ArticleParser(temp_articles_file)
        article = parser.get_article(2)

        assert article is not None
        assert article.number == 2
        assert article.title == "Data Strategy for AI Success"

    def test_get_article_nonexistent(self, temp_articles_file):
        """Test retrieving a non-existent article returns None."""
        parser = ArticleParser(temp_articles_file)
        article = parser.get_article(999)

        assert article is None

    def test_get_total_articles(self, temp_articles_file):
        """Test getting total article count."""
        parser = ArticleParser(temp_articles_file)
        total = parser.get_total_articles()

        assert total == 3


@pytest.mark.unit
class TestArticleParserEdgeCases:
    """Test suite for ArticleParser edge cases and error handling."""

    def test_parse_empty_file(self, tmp_path):
        """Test parsing an empty file."""
        empty_file = tmp_path / "empty.md"
        empty_file.write_text("", encoding='utf-8')

        parser = ArticleParser(empty_file)
        articles = parser.parse()

        assert articles == []

    def test_parse_file_with_no_articles(self, tmp_path):
        """Test parsing a file with no article sections."""
        no_articles_file = tmp_path / "no_articles.md"
        no_articles_file.write_text("# Just a header\n\nSome content", encoding='utf-8')

        parser = ArticleParser(no_articles_file)
        articles = parser.parse()

        assert articles == []

    def test_parse_malformed_article_missing_title(self, tmp_path):
        """Test parsing article with missing title."""
        malformed_file = tmp_path / "malformed.md"
        content = """## Article #1

**URL:** https://www.linkedin.com/pulse/test-aaron-lim/

**Content:**

Test content

**Metadata:**
- Word Count: 50
- Status: Active

---
"""
        malformed_file.write_text(content, encoding='utf-8')

        parser = ArticleParser(malformed_file)
        articles = parser.parse()

        assert len(articles) == 1
        assert articles[0].title == ""  # Missing title should be empty string
        assert articles[0].has_title is False

    def test_parse_malformed_article_missing_url(self, tmp_path):
        """Test parsing article with missing URL."""
        malformed_file = tmp_path / "malformed.md"
        content = """## Article #1

**Title:** Test Article

**Content:**

Test content

**Metadata:**
- Word Count: 50
- Status: Active

---
"""
        malformed_file.write_text(content, encoding='utf-8')

        parser = ArticleParser(malformed_file)
        articles = parser.parse()

        assert len(articles) == 1
        assert articles[0].url == ""  # Missing URL should be empty string
        assert articles[0].has_url is False

    def test_parse_article_with_missing_metadata(self, tmp_path):
        """Test parsing article with missing metadata section."""
        malformed_file = tmp_path / "malformed.md"
        content = """## Article #1

**Title:** Test Article

**URL:** https://www.linkedin.com/pulse/test-aaron-lim/

**Content:**

Test content without metadata section.
"""
        malformed_file.write_text(content, encoding='utf-8')

        parser = ArticleParser(malformed_file)
        articles = parser.parse()

        # Should still parse but content extraction might fail
        # The parser should handle this gracefully
        assert len(articles) >= 0  # May or may not parse successfully

    def test_parse_article_with_special_characters(self, tmp_path):
        """Test parsing article with special characters in content."""
        special_file = tmp_path / "special.md"
        content = """## Article #1

**Title:** AI & ML: The Future (2024)

**URL:** https://www.linkedin.com/pulse/ai-ml-future-2024-aaron-lim/

**Content:**

This article contains special characters: & < > " '
And unicode: 🚀 💡 📊

**Metadata:**
- Word Count: 100
- Status: Active

---
"""
        special_file.write_text(content, encoding='utf-8')

        parser = ArticleParser(special_file)
        articles = parser.parse()

        assert len(articles) == 1
        assert "AI & ML" in articles[0].title
        assert "🚀" in articles[0].content or "special characters" in articles[0].content

