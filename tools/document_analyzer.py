"""
Document Analyzer for CoreAI Newsletter Articles
Analyzes the structure and format of the source document to validate
it's ready for the Tweet Processor system.
"""

import re
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class Article:
    """Represents a single newsletter article."""
    number: int
    title: str
    url: str
    content: str
    word_count: int
    has_url: bool
    has_title: bool


class DocumentAnalyzer:
    """Analyzes document structure and extracts articles."""
    
    def __init__(self, document_text: str):
        self.document_text = document_text
        self.articles: List[Article] = []
        self.issues: List[str] = []
        self.warnings: List[str] = []
    
    def analyze(self) -> Dict[str, Any]:
        """
        Analyze the document and return a comprehensive report.
        
        Returns:
            Dictionary containing analysis results, issues, and recommendations
        """
        # Extract articles
        self._extract_articles()
        
        # Validate structure
        self._validate_structure()
        
        # Generate report
        return self._generate_report()
    
    def _extract_articles(self):
        """Extract all articles from the document."""
        # Pattern to match "Article #N" or "Article N"
        article_pattern = r'Article\s*#?(\d+)'
        
        # Split document by article markers
        parts = re.split(article_pattern, self.document_text, flags=re.IGNORECASE)
        
        # First part is before any article (skip it)
        # Then we have pairs of (article_number, article_content)
        for i in range(1, len(parts), 2):
            if i + 1 < len(parts):
                article_num = int(parts[i])
                article_content = parts[i + 1].strip()
                
                # Extract title
                title = self._extract_title(article_content)
                
                # Extract URL
                url = self._extract_url(article_content)
                
                # Get content (everything after URL)
                content = self._extract_content(article_content)
                
                # Create article object
                article = Article(
                    number=article_num,
                    title=title if title else "NO TITLE FOUND",
                    url=url if url else "NO URL FOUND",
                    content=content,
                    word_count=len(content.split()),
                    has_url=bool(url),
                    has_title=bool(title)
                )
                
                self.articles.append(article)
    
    def _extract_title(self, text: str) -> str:
        """Extract article title from text."""
        lines = text.split('\n')
        
        # Look for "Title:" prefix
        for line in lines[:10]:  # Check first 10 lines
            if line.strip().lower().startswith('title:'):
                return line.split(':', 1)[1].strip()
            # If no "Title:" prefix, first non-empty line might be title
            elif line.strip() and not line.strip().startswith('http'):
                # Check if it looks like a title (not too long, no URL)
                if len(line.strip()) < 200 and 'http' not in line.lower():
                    return line.strip()
        
        return ""
    
    def _extract_url(self, text: str) -> str:
        """Extract LinkedIn URL from text."""
        # Pattern for LinkedIn URLs
        url_pattern = r'https?://(?:www\.)?linkedin\.com/(?:pulse|posts)/[^\s]+'
        
        matches = re.findall(url_pattern, text)
        if matches:
            return matches[0]
        
        # Also check for "URL:" prefix
        lines = text.split('\n')
        for line in lines[:15]:  # Check first 15 lines
            if line.strip().lower().startswith('url:'):
                url_text = line.split(':', 1)[1].strip()
                # Extract URL from this line
                url_matches = re.findall(url_pattern, url_text)
                if url_matches:
                    return url_matches[0]
        
        return ""
    
    def _extract_content(self, text: str) -> str:
        """Extract main article content (after title and URL)."""
        lines = text.split('\n')
        
        # Skip first few lines (title, URL, separators)
        content_lines = []
        skip_count = 0
        
        for line in lines:
            # Skip title line
            if line.strip().lower().startswith('title:'):
                skip_count += 1
                continue
            # Skip URL line
            if line.strip().lower().startswith('url:') or 'linkedin.com' in line.lower():
                skip_count += 1
                continue
            # Skip separator lines
            if line.strip() in ['---', '===', '***']:
                skip_count += 1
                continue
            # Skip empty lines at the beginning
            if not line.strip() and skip_count < 5:
                skip_count += 1
                continue
            
            # Start collecting content
            content_lines.append(line)
        
        return '\n'.join(content_lines).strip()
    
    def _validate_structure(self):
        """Validate document structure and identify issues."""
        if not self.articles:
            self.issues.append("❌ No articles found in document")
            return
        
        # Check for sequential numbering
        expected_numbers = list(range(1, len(self.articles) + 1))
        actual_numbers = [a.number for a in self.articles]
        
        if actual_numbers != expected_numbers:
            self.issues.append(
                f"❌ Article numbering is not sequential. "
                f"Expected: {expected_numbers}, Found: {actual_numbers}"
            )
        
        # Check each article
        for article in self.articles:
            # Check for missing title
            if not article.has_title:
                self.issues.append(f"❌ Article #{article.number}: Missing title")
            
            # Check for missing URL
            if not article.has_url:
                self.issues.append(f"❌ Article #{article.number}: Missing LinkedIn URL")
            
            # Check for very short content
            if article.word_count < 50:
                self.warnings.append(
                    f"⚠️  Article #{article.number}: Very short content ({article.word_count} words). "
                    "May not have enough material for tweet generation."
                )
            
            # Check for very long content
            if article.word_count > 5000:
                self.warnings.append(
                    f"⚠️  Article #{article.number}: Very long content ({article.word_count} words). "
                    "Consider summarizing for better LLM processing."
                )
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive analysis report."""
        return {
            "summary": {
                "total_articles": len(self.articles),
                "articles_with_titles": sum(1 for a in self.articles if a.has_title),
                "articles_with_urls": sum(1 for a in self.articles if a.has_url),
                "total_word_count": sum(a.word_count for a in self.articles),
                "avg_word_count": sum(a.word_count for a in self.articles) / len(self.articles) if self.articles else 0,
            },
            "articles": [
                {
                    "number": a.number,
                    "title": a.title,
                    "url": a.url,
                    "word_count": a.word_count,
                    "has_title": a.has_title,
                    "has_url": a.has_url,
                    "content_preview": a.content[:200] + "..." if len(a.content) > 200 else a.content
                }
                for a in self.articles
            ],
            "issues": self.issues,
            "warnings": self.warnings,
            "status": "✅ READY" if not self.issues else "❌ NEEDS FIXES"
        }
    
    def print_report(self):
        """Print a formatted analysis report."""
        report = self._generate_report()
        
        print("=" * 80)
        print("📄 COREAI NEWSLETTER DOCUMENT ANALYSIS REPORT")
        print("=" * 80)
        print()
        
        # Summary
        print("📊 SUMMARY")
        print("-" * 80)
        print(f"Total Articles Found: {report['summary']['total_articles']}")
        print(f"Articles with Titles: {report['summary']['articles_with_titles']}")
        print(f"Articles with URLs: {report['summary']['articles_with_urls']}")
        print(f"Total Word Count: {report['summary']['total_word_count']:,}")
        print(f"Average Words per Article: {report['summary']['avg_word_count']:.0f}")
        print()
        
        # Issues
        if report['issues']:
            print("❌ ISSUES (Must Fix)")
            print("-" * 80)
            for issue in report['issues']:
                print(f"  {issue}")
            print()
        
        # Warnings
        if report['warnings']:
            print("⚠️  WARNINGS (Review Recommended)")
            print("-" * 80)
            for warning in report['warnings']:
                print(f"  {warning}")
            print()
        
        # Article List
        print("📝 ARTICLES")
        print("-" * 80)
        for article_info in report['articles']:
            status = "✅" if article_info['has_title'] and article_info['has_url'] else "❌"
            print(f"{status} Article #{article_info['number']}")
            print(f"   Title: {article_info['title'][:70]}...")
            print(f"   URL: {article_info['url'][:70]}...")
            print(f"   Words: {article_info['word_count']}")
            print()
        
        # Final Status
        print("=" * 80)
        print(f"FINAL STATUS: {report['status']}")
        print("=" * 80)
        
        return report


def analyze_document(file_path: str):
    """
    Analyze a document file and print the report.
    
    Args:
        file_path: Path to the document file (txt, docx, or pdf)
    """
    # Read document based on file type
    if file_path.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    elif file_path.endswith('.docx'):
        # Requires python-docx
        from docx import Document
        doc = Document(file_path)
        text = '\n'.join([para.text for para in doc.paragraphs])
    elif file_path.endswith('.pdf'):
        # Requires PyPDF2 or pdfplumber
        import pdfplumber
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    else:
        raise ValueError(f"Unsupported file type: {file_path}")
    
    # Analyze
    analyzer = DocumentAnalyzer(text)
    report = analyzer.print_report()
    
    return report


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python document_analyzer.py <path_to_document>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    analyze_document(file_path)

