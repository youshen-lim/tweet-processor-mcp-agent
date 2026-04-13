"""
URL Validation Utility for Tweet Processor
Provides comprehensive URL validation and integrity checking.
"""

import logging
from typing import Dict, List, Any, Optional


class URLValidator:
    """
    Utility class for validating article URLs and ensuring data integrity.

    This validator dynamically handles any number of articles (1-N) and provides:
    - URL format validation (LinkedIn pulse URLs with proper patterns)
    - Duplicate URL detection across all articles
    - Required field validation (number, title, url key existence)
    - Special case handling (e.g., Article #5 can have empty URL)
    - Comprehensive validation reporting

    Note: URL validation uses format patterns instead of exact matching,
    allowing flexibility while ensuring URLs follow expected LinkedIn pulse patterns.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize URL validator.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
    
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
    
    def validate_url_format(self, url: str, article_number: Optional[int] = None) -> bool:
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
    
    def validate_url_uniqueness(self, articles: List[Dict[str, Any]]) -> bool:
        """
        Validate that all article URLs are unique.
        
        Args:
            articles: List of article data
            
        Returns:
            bool: True if all URLs are unique
            
        Raises:
            ValueError: If duplicate URLs are found
        """
        urls = [article.get('url') for article in articles if article.get('url')]
        
        if len(urls) != len(set(urls)):
            duplicates = [url for url in urls if urls.count(url) > 1]
            raise ValueError(f"Duplicate URLs found: {list(set(duplicates))}")
        
        return True
    
    def validate_articles_data(self, articles: List[Dict[str, Any]], expected_count: Optional[int] = None) -> Dict[str, Any]:
        """
        Comprehensive validation of articles data.

        This method dynamically validates any number of articles (1-N) while maintaining
        all validation rules including format checking, duplicate detection, and special
        case handling (e.g., Article #5 can have empty URL).

        Args:
            articles: List of article data to validate
            expected_count: Optional expected number of articles. If None, accepts any count >= 1.

        Returns:
            Dict with validation results including:
                - total_articles: Total number of articles processed
                - valid_articles: Number of articles that passed validation
                - validation_errors: List of validation error messages
                - validation_warnings: List of validation warning messages

        Raises:
            ValueError: If validation fails (no articles, count mismatch, or validation errors)
        """
        validation_results = {
            'total_articles': len(articles),
            'valid_articles': 0,
            'validation_errors': [],
            'validation_warnings': []
        }

        # Check for empty articles list
        if not articles:
            raise ValueError("No articles found in data")

        # Validate article count if expected_count is specified
        if expected_count is not None and len(articles) != expected_count:
            raise ValueError(f"Expected {expected_count} articles, found {len(articles)}")

        # Log validation start
        self.logger.info(f"Starting validation for {len(articles)} article(s)")

        # Validate each article
        for article in articles:
            article_number = article.get('number')
            article_url = article.get('url')
            article_title = article.get('title')
            
            try:
                # Check required fields
                if not article_number:
                    raise ValueError(f"Article missing 'number' field: {article}")

                if not article_title:
                    raise ValueError(f"Article #{article_number} missing 'title' field")

                # Check if 'url' key exists (not if it's empty, as Article #5 can have empty URL)
                if 'url' not in article:
                    raise ValueError(f"Article #{article_number} missing 'url' field")

                # Article #5 is allowed to have empty URL (special case)
                if article_number == 5 and (not article_url or not article_url.strip()):
                    self.logger.info(f"✅ Article #{article_number} has no URL (expected for incomplete article)")
                    validation_results['valid_articles'] += 1
                    continue

                # Validate URL format and mapping for other articles
                self.validate_url_format(article_url, article_number)
                self.validate_article_url(article_number, article_url)

                validation_results['valid_articles'] += 1
                
            except ValueError as e:
                error_msg = f"Article #{article_number} validation failed: {str(e)}"
                validation_results['validation_errors'].append(error_msg)
                self.logger.error(error_msg)
        
        # Check for duplicates
        try:
            self.validate_url_uniqueness(articles)
        except ValueError as e:
            validation_results['validation_errors'].append(str(e))
        
        # Check for duplicate article numbers
        article_numbers = [article.get('number') for article in articles if article.get('number')]
        if len(set(article_numbers)) != len(article_numbers):
            error_msg = f"Duplicate article numbers found: {article_numbers}"
            validation_results['validation_errors'].append(error_msg)
        
        # Raise if any errors found
        if validation_results['validation_errors']:
            error_summary = "\n".join(validation_results['validation_errors'])
            raise ValueError(f"Article validation failed:\n{error_summary}")
        
        return validation_results
    
    def generate_validation_report(self, articles: List[Dict[str, Any]]) -> str:
        """
        Generate a detailed validation report.
        
        Args:
            articles: List of article data
            
        Returns:
            str: Formatted validation report
        """
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("URL VALIDATION REPORT")
        report_lines.append("=" * 60)
        
        for article in articles:
            article_number = article.get('number', 'Unknown')
            article_url = article.get('url', 'Missing')
            article_title = article.get('title', 'Unknown')
            
            report_lines.append(f"Article #{article_number}: {article_title}")
            report_lines.append(f"  URL: {article_url}")
            
            try:
                if article.get('url'):
                    self.validate_url_format(article_url, article_number)
                    self.validate_article_url(article_number, article_url)
                    report_lines.append(f"  Status: ✅ VALID")
                else:
                    report_lines.append(f"  Status: ❌ MISSING URL")
            except ValueError as e:
                report_lines.append(f"  Status: ❌ INVALID - {str(e)}")
            
            report_lines.append("")
        
        report_lines.append("=" * 60)
        
        return "\n".join(report_lines)
    
    def log_validation_report(self, articles: List[Dict[str, Any]]) -> None:
        """
        Log a comprehensive validation report.
        
        Args:
            articles: List of article data
        """
        report = self.generate_validation_report(articles)
        for line in report.split('\n'):
            if line.strip():
                if '✅' in line:
                    self.logger.info(line)
                elif '❌' in line:
                    self.logger.error(line)
                else:
                    self.logger.info(line)


# Convenience functions for direct usage
def validate_article_url(article_number: int, article_url: str, logger: Optional[logging.Logger] = None) -> bool:
    """Convenience function to validate a single article URL."""
    validator = URLValidator(logger)
    return validator.validate_article_url(article_number, article_url)


def validate_articles_data(articles: List[Dict[str, Any]], expected_count: Optional[int] = None, logger: Optional[logging.Logger] = None) -> Dict[str, Any]:
    """
    Convenience function to validate articles data.

    Args:
        articles: List of article data to validate
        expected_count: Optional expected number of articles. If None, accepts any count >= 1.
        logger: Optional logger instance

    Returns:
        Dict with validation results
    """
    validator = URLValidator(logger)
    return validator.validate_articles_data(articles, expected_count)
