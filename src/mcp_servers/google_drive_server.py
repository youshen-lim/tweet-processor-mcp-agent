"""
Google Drive MCP Server
Provides tools for reading documents from Google Drive.
"""

import os
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
from docx import Document as DocxDocument

# MCP Server setup (using LastMile AI's MCP framework)
from mcp.server import Server
from mcp.types import Tool, TextContent

# Initialize MCP server
mcp = Server("google-drive-server")

# Google Drive configuration
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
DOCUMENT_ID = "1kZMdOrmI5JZR65jvZbzGZ9VKKvGlLqFO"


@dataclass
class Article:
    """Represents a single newsletter article."""
    number: int
    title: str
    url: str
    content: str
    word_count: int
    has_title: bool
    has_url: bool


class GoogleDriveClient:
    """Client for interacting with Google Drive API."""
    
    def __init__(self, credentials_path: Optional[str] = None):
        """Initialize Google Drive client."""
        self.credentials_path = credentials_path or os.getenv('GOOGLE_CREDENTIALS_PATH')
        self.service = None
        
    def authenticate(self):
        """Authenticate with Google Drive API."""
        if not self.credentials_path:
            raise ValueError("Google credentials path not provided")
            
        credentials = service_account.Credentials.from_service_account_file(
            self.credentials_path, scopes=SCOPES
        )
        self.service = build('drive', 'v3', credentials=credentials)
        
    def download_document(self, document_id: str) -> bytes:
        """Download document from Google Drive."""
        if not self.service:
            self.authenticate()
            
        # Export as Word document (.docx)
        request = self.service.files().export_media(
            fileId=document_id,
            mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
        file_handle = io.BytesIO()
        downloader = MediaIoBaseDownload(file_handle, request)
        
        done = False
        while not done:
            status, done = downloader.next_chunk()
            
        file_handle.seek(0)
        return file_handle.read()
    
    def read_document_text(self, document_id: str) -> str:
        """Read text content from a Word document."""
        doc_bytes = self.download_document(document_id)
        
        # Parse Word document
        doc_file = io.BytesIO(doc_bytes)
        doc = DocxDocument(doc_file)
        
        # Extract all text
        full_text = []
        for paragraph in doc.paragraphs:
            full_text.append(paragraph.text)
            
        return '\n'.join(full_text)


class DocumentParser:
    """Parser for CoreAI Newsletter documents."""
    
    def __init__(self, document_text: str):
        """Initialize parser with document text."""
        self.document_text = document_text
        self.articles: List[Article] = []
        
    def parse(self) -> List[Article]:
        """Parse document and extract all articles."""
        self._extract_articles()
        return self.articles
    
    def _extract_articles(self):
        """Extract all articles from the document."""
        # Pattern to match article headers
        # Format: Article #N\n\nArticle #N Title: ...\n\nArticle #N URL: ...
        
        # Split by "Article #" markers
        article_sections = re.split(r'(?=Article\s*#\d+\s*\n)', self.document_text)
        
        for section in article_sections:
            if not section.strip():
                continue
                
            article = self._parse_article_section(section)
            if article:
                self.articles.append(article)
    
    def _parse_article_section(self, section: str) -> Optional[Article]:
        """Parse a single article section."""
        # Extract article number
        number_match = re.search(r'Article\s*#(\d+)', section, re.IGNORECASE)
        if not number_match:
            return None
        article_num = int(number_match.group(1))
        
        # Extract title
        title_match = re.search(
            rf'Article\s*#{article_num}\s+Title:\s*(.+?)(?=\n)',
            section,
            re.IGNORECASE
        )
        title = title_match.group(1).strip() if title_match else ""
        
        # Extract URL
        url_match = re.search(
            rf'Article\s*#{article_num}\s+URL:\s*(.+?)(?=\n)',
            section,
            re.IGNORECASE
        )
        url = url_match.group(1).strip() if url_match else ""
        
        # Extract content (everything after URL line)
        content_match = re.search(
            rf'Article\s*#{article_num}\s+URL:.*?\n\s*\n(.+?)(?=Article\s*#\d+|$)',
            section,
            re.DOTALL | re.IGNORECASE
        )
        content = content_match.group(1).strip() if content_match else ""
        
        # Clean up content (remove excessive whitespace)
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        
        return Article(
            number=article_num,
            title=title,
            url=url,
            content=content,
            word_count=len(content.split()),
            has_title=bool(title),
            has_url=bool(url)
        )


# MCP Tools

@mcp.tool()
async def read_newsletter_document(document_id: str = DOCUMENT_ID) -> str:
    """
    Read the CoreAI Newsletter document from Google Drive.
    
    Args:
        document_id: Google Drive document ID (default: configured document)
        
    Returns:
        Full text content of the document
    """
    client = GoogleDriveClient()
    text = client.read_document_text(document_id)
    return text


@mcp.tool()
async def parse_newsletter_articles(document_id: str = DOCUMENT_ID) -> List[Dict[str, Any]]:
    """
    Parse CoreAI Newsletter document and extract all articles.
    
    Args:
        document_id: Google Drive document ID (default: configured document)
        
    Returns:
        List of articles with number, title, URL, content, and metadata
    """
    # Read document
    client = GoogleDriveClient()
    text = client.read_document_text(document_id)
    
    # Parse articles
    parser = DocumentParser(text)
    articles = parser.parse()
    
    # Convert to dict format
    return [
        {
            "number": article.number,
            "title": article.title,
            "url": article.url,
            "content": article.content,
            "word_count": article.word_count,
            "has_title": article.has_title,
            "has_url": article.has_url
        }
        for article in articles
    ]


@mcp.tool()
async def get_article_by_number(article_number: int, document_id: str = DOCUMENT_ID) -> Dict[str, Any]:
    """
    Get a specific article by its number.
    
    Args:
        article_number: Article number to retrieve
        document_id: Google Drive document ID (default: configured document)
        
    Returns:
        Article data with number, title, URL, content, and metadata
    """
    articles = await parse_newsletter_articles(document_id)
    
    for article in articles:
        if article["number"] == article_number:
            return article
            
    raise ValueError(f"Article #{article_number} not found")


@mcp.tool()
async def validate_document_structure(document_id: str = DOCUMENT_ID) -> Dict[str, Any]:
    """
    Validate the structure of the newsletter document.
    
    Args:
        document_id: Google Drive document ID (default: configured document)
        
    Returns:
        Validation report with article count, issues, and warnings
    """
    articles = await parse_newsletter_articles(document_id)
    
    issues = []
    warnings = []
    
    # Check for sequential numbering
    expected_num = 1
    for article in articles:
        if article["number"] != expected_num:
            issues.append(f"Article numbering gap: expected #{expected_num}, found #{article['number']}")
        expected_num = article["number"] + 1
    
    # Check for missing titles or URLs
    for article in articles:
        if not article["has_title"]:
            warnings.append(f"Article #{article['number']} is missing a title")
        if not article["has_url"]:
            warnings.append(f"Article #{article['number']} is missing a URL")
        if article["word_count"] < 50:
            warnings.append(f"Article #{article['number']} has very short content ({article['word_count']} words)")
    
    return {
        "total_articles": len(articles),
        "articles_with_titles": sum(1 for a in articles if a["has_title"]),
        "articles_with_urls": sum(1 for a in articles if a["has_url"]),
        "total_words": sum(a["word_count"] for a in articles),
        "avg_words_per_article": sum(a["word_count"] for a in articles) / len(articles) if articles else 0,
        "issues": issues,
        "warnings": warnings,
        "status": "valid" if not issues else "invalid"
    }


# Server lifecycle
@mcp.server_lifecycle()
async def on_startup():
    """Initialize server on startup."""
    print("Google Drive MCP Server started")
    print(f"Configured document ID: {DOCUMENT_ID}")


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()

