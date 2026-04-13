"""
Test script for ArticleParser - verifies local Markdown file parsing.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


def test_article_parser():
    """Test the ArticleParser with data/articles.md."""
    
    print("=" * 80)
    print("ARTICLE PARSER TEST")
    print("=" * 80)
    print()
    
    # Import parser
    print("📚 Importing ArticleParser...")
    try:
        from parsers.article_parser import ArticleParser
        print("✓ ArticleParser imported successfully")
    except ImportError as e:
        print(f"❌ ERROR: Failed to import ArticleParser")
        print(f"   Error: {e}")
        return False
    print()
    
    # Initialize parser
    print("📂 Initializing parser...")
    try:
        parser = ArticleParser()
        print(f"✓ Parser initialized")
        print(f"   Reading from: {parser.file_path}")
    except FileNotFoundError as e:
        print(f"❌ ERROR: {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR: Failed to initialize parser")
        print(f"   Error: {e}")
        return False
    print()
    
    # Parse articles
    print("🔍 Parsing articles...")
    try:
        articles = parser.parse()
        print(f"✓ Found {len(articles)} articles")
    except Exception as e:
        print(f"❌ ERROR: Failed to parse articles")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    print()
    
    # Verify article count
    print("📊 Article Verification:")
    expected_count = 15
    if len(articles) == expected_count:
        print(f"✅ SUCCESS: Found all {expected_count} articles!")
    else:
        print(f"⚠️  WARNING: Expected {expected_count} articles, found {len(articles)}")
    print()
    
    # Display article summary
    print("📋 Article Summary:")
    print("-" * 80)
    
    total_words = 0
    articles_with_issues = []
    
    for article in articles:
        # Check for issues
        issues = []
        if not article.has_title:
            issues.append("NO TITLE")
        if not article.has_url:
            issues.append("NO URL")
        if not article.has_content:
            issues.append("NO CONTENT")
        
        if issues:
            articles_with_issues.append((article.number, issues))
        
        # Display summary
        title_preview = article.title[:60] + "..." if len(article.title) > 60 else article.title
        url_status = "✓" if article.has_url else "✗"
        title_status = "✓" if article.has_title else "✗"
        content_status = "✓" if article.has_content else "✗"
        
        print(f"Article #{article.number:2d}: {title_status} Title | {url_status} URL | {content_status} {article.word_count:,} words")
        if issues:
            print(f"             ⚠️  Issues: {', '.join(issues)}")
        
        total_words += article.word_count
    
    print("-" * 80)
    print(f"Total word count: {total_words:,}")
    print()
    
    # Report issues
    if articles_with_issues:
        print("⚠️  Articles with Issues:")
        for article_num, issues in articles_with_issues:
            print(f"   Article #{article_num}: {', '.join(issues)}")
        print()
    
    # Test get_article method
    print("🔍 Testing get_article() method...")
    test_article = parser.get_article(1)
    if test_article:
        print(f"✓ Successfully retrieved Article #1")
        print(f"   Title: {test_article.title[:60]}...")
    else:
        print(f"❌ ERROR: Failed to retrieve Article #1")
    print()
    
    # Test get_total_articles method
    print("🔍 Testing get_total_articles() method...")
    total = parser.get_total_articles()
    print(f"✓ Total articles: {total}")
    print()
    
    # Final verdict
    print("=" * 80)
    if len(articles) == expected_count and not articles_with_issues:
        print("✅ ALL TESTS PASSED")
        print("=" * 80)
        print()
        print("The ArticleParser is working correctly!")
        print("All 15 articles parsed successfully with no issues.")
        print()
        return True
    elif len(articles) == expected_count:
        print("⚠️  TESTS PASSED WITH WARNINGS")
        print("=" * 80)
        print()
        print(f"Found all {expected_count} articles, but some have issues.")
        print("Please review the articles with issues above.")
        print()
        return True
    else:
        print("❌ TESTS FAILED")
        print("=" * 80)
        print()
        print(f"Expected {expected_count} articles but found {len(articles)}")
        print()
        return False


def main():
    success = test_article_parser()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

