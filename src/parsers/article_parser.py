"""
Article Parser for Local Markdown Files

Parses newsletter articles from local Markdown files (data/articles.md).
This replaces the Google Drive-based document parser with a simpler,
file-based approach.
"""

import re
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class Article:
    """Represents a newsletter article."""
    number: int
    title: str
    url: str
    content: str
    word_count: int
    status: str = "Active"

    @property
    def has_title(self) -> bool:
        """Check if article has a valid title."""
        return bool(self.title and self.title.strip())

    @property
    def has_url(self) -> bool:
        """Check if article has a valid URL."""
        return bool(self.url and self.url.strip())

    @property
    def has_content(self) -> bool:
        """Check if article has valid content."""
        return bool(self.content and self.content.strip())


class ArticleParser:
    """Parser for local Markdown article files."""

    def __init__(self, file_path: Optional[Path] = None):
        """
        Initialize parser.

        Args:
            file_path: Path to articles.md file. Defaults to data/articles.md
        """
        if file_path is None:
            # Default to data/articles.md in repository root
            repo_root = Path(__file__).parent.parent.parent
            file_path = repo_root / 'data' / 'articles.md'

        self.file_path = Path(file_path)

        if not self.file_path.exists():
            raise FileNotFoundError(
                f"Articles file not found: {self.file_path}\n"
                f"Please ensure data/articles.md exists in the repository."
            )

    def parse(self) -> List[Article]:
        """
        Parse articles from Markdown file.

        Returns:
            List of Article objects sorted by article number
        """
        content = self.file_path.read_text(encoding='utf-8')
        return self._parse_markdown(content)

    def _parse_markdown(self, content: str) -> List[Article]:
        """Parse Markdown content into Article objects."""
        articles = []

        # Split by article headers (## Article #N)
        article_pattern = r'^## Article #(\d+)$'
        sections = re.split(article_pattern, content, flags=re.MULTILINE)

        # sections[0] is the header before first article
        # sections[1] is article number, sections[2] is article content
        # sections[3] is next article number, sections[4] is next article content, etc.

        for i in range(1, len(sections), 2):
            if i + 1 >= len(sections):
                break

            article_num = int(sections[i])
            article_content = sections[i + 1]

            article = self._parse_article_section(article_num, article_content)
            if article:
                articles.append(article)

        return sorted(articles, key=lambda a: a.number)

    def _parse_article_section(self, number: int, content: str) -> Optional[Article]:
        """Parse a single article section."""

        # Extract title
        title_match = re.search(r'\*\*Title:\*\*\s*(.+?)(?:\n|$)', content)
        title = title_match.group(1).strip() if title_match else ""

        # Extract URL
        url_match = re.search(r'\*\*URL:\*\*\s*(.+?)(?:\n|$)', content)
        url = url_match.group(1).strip() if url_match else ""

        # Extract content (between **Content:** and **Metadata:**)
        content_match = re.search(
            r'\*\*Content:\*\*\s*\n\n(.+?)\n\n\*\*Metadata:\*\*',
            content,
            re.DOTALL
        )
        article_content = content_match.group(1).strip() if content_match else ""

        # Extract word count from metadata
        word_count_match = re.search(r'- Word Count:\s*(\d+)', content)
        word_count = int(word_count_match.group(1)) if word_count_match else len(article_content.split())

        # Extract status
        status_match = re.search(r'- Status:\s*(.+?)(?:\n|$)', content)
        status = status_match.group(1).strip() if status_match else "Active"

        return Article(
            number=number,
            title=title,
            url=url,
            content=article_content,
            word_count=word_count,
            status=status
        )

    def get_article(self, number: int) -> Optional[Article]:
        """
        Get a specific article by number.

        Args:
            number: Article number to retrieve

        Returns:
            Article object if found, None otherwise
        """
        articles = self.parse()
        for article in articles:
            if article.number == number:
                return article
        return None

    def get_total_articles(self) -> int:
        """Get total number of articles."""
        return len(self.parse())

