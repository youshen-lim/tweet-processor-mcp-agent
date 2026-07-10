#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convert data/articles.docx -> data/articles.md

The Tweet Processor runtime only reads the Markdown file (data/articles.md);
the .docx is never parsed by the app. This script bridges that gap: it reads
the Word document, extracts each article, and writes the exact Markdown format
that src/parsers/article_parser.py expects.

Expected .docx structure (one block per article):
    Article #N                          <- Heading 1 paragraph (article boundary)
    Article #N Title: <title>           <- Normal paragraph
    Article #N URL: : <url>             <- Normal paragraph (note the double colon)
    <body paragraph 1>
    <body paragraph 2>
    ...

Output Markdown format (per article):
    ## Article #N

    **Title:** <title>

    **URL:** <url>

    **Content:**

    <content>

    **Metadata:**
    - Word Count: <n>
    - Status: Active

    ---

Usage:
    python scripts/convert_docx_to_md.py                 # convert (with backup)
    python scripts/convert_docx_to_md.py --dry-run       # report only, write nothing
    python scripts/convert_docx_to_md.py --clear-cache   # also empty articles_cache in workflow_state.json
    python scripts/convert_docx_to_md.py --input data/articles.docx --output data/articles.md
    python scripts/convert_docx_to_md.py --no-backup     # overwrite without timestamped backup
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# Paragraph-classifying patterns (tolerant of spacing and single/double colons)
ARTICLE_HEADING_RE = re.compile(r'^Article\s*#\s*(\d+)\s*$', re.IGNORECASE)
TITLE_RE = re.compile(r'^Article\s*#\s*\d+\s*Title\s*:\s*(.*)$', re.IGNORECASE)
URL_RE = re.compile(r'^Article\s*#\s*\d+\s*URL\s*:\s*:?\s*(.*)$', re.IGNORECASE)


@dataclass
class ParsedArticle:
    number: int
    title: str = ""
    url: str = ""
    content_paragraphs: List[str] = field(default_factory=list)

    @property
    def content(self) -> str:
        return "\n".join(self.content_paragraphs).strip()

    @property
    def word_count(self) -> int:
        return len(self.content.split())


def load_paragraphs(docx_path: Path):
    """Return a list of (style_name, text) tuples for every body paragraph.

    Raises ImportError if python-docx is unavailable, so callers (the CLI or
    the workflow's in-process sync) can decide how to handle it rather than the
    process being killed by a hard sys.exit().
    """
    from docx import Document  # raises ImportError if python-docx is missing
    doc = Document(docx_path)
    return [((p.style.name if p.style else ""), p.text) for p in doc.paragraphs]


def is_article_heading(style: str, text: str) -> Optional[int]:
    """Return the article number if this paragraph starts a new article, else None."""
    m = ARTICLE_HEADING_RE.match(text.strip())
    if not m:
        return None
    # Accept either a real heading style or a bare "Article #N" line, but reject
    # a body line that merely starts that way (those are caught by the strict
    # full-string regex above, so any match here is a genuine boundary).
    return int(m.group(1))


def parse_docx(docx_path: Path) -> List[ParsedArticle]:
    """Parse the .docx into a list of ParsedArticle objects."""
    paragraphs = load_paragraphs(docx_path)
    articles: List[ParsedArticle] = []
    current: Optional[ParsedArticle] = None

    for style, raw in paragraphs:
        text = raw.strip()

        num = is_article_heading(style, raw)
        if num is not None:
            current = ParsedArticle(number=num)
            articles.append(current)
            continue

        if current is None:
            # Preamble before the first article heading; ignore.
            continue

        if not text:
            continue

        title_m = TITLE_RE.match(text)
        if title_m and not current.title:
            current.title = title_m.group(1).strip()
            continue

        url_m = URL_RE.match(text)
        if url_m and not current.url:
            current.url = url_m.group(1).strip()
            continue

        current.content_paragraphs.append(text)

    return articles


def build_markdown(articles: List[ParsedArticle]) -> str:
    """Render articles into the exact Markdown format the parser expects."""
    header = (
        "# Newsletter Articles\n\n"
        "This file contains all newsletter articles for the Tweet Processor.\n\n"
        "**Format Guidelines:**\n"
        "- Each article starts with `## Article #N`\n"
        "- Required fields: Title, URL, Content\n"
        "- Optional fields: Metadata (word count, status)\n"
        "- Articles are separated by `---`\n\n"
        "**Editing:**\n"
        "- This file is generated from `data/articles.docx` by "
        "`scripts/convert_docx_to_md.py`\n"
        "- Re-run the converter after updating the .docx, then clear the "
        "`articles_cache` in `workflow_state.json`\n\n"
        "---\n\n"
    )

    blocks = []
    for a in sorted(articles, key=lambda x: x.number):
        block = (
            f"## Article #{a.number}\n\n"
            f"**Title:** {a.title}\n\n"
            f"**URL:** {a.url}\n\n"
            f"**Content:**\n\n"
            f"{a.content}\n\n"
            f"**Metadata:**\n"
            f"- Word Count: {a.word_count}\n"
            f"- Status: Active\n\n"
            f"---\n"
        )
        blocks.append(block)

    return header + "\n".join(blocks) + "\n"


def report(articles: List[ParsedArticle]) -> None:
    print("=" * 80)
    print("PARSED ARTICLES")
    print("=" * 80)
    issues = 0
    for a in sorted(articles, key=lambda x: x.number):
        flags = []
        if not a.title:
            flags.append("NO TITLE")
        if not a.url:
            flags.append("NO URL")
        if a.word_count == 0:
            flags.append("NO CONTENT")
        flag_str = ("  <-- " + ", ".join(flags)) if flags else ""
        issues += len(flags)
        title_preview = (a.title[:58] + "...") if len(a.title) > 58 else a.title
        print(f"#{a.number:>2}  {a.word_count:>5} words  {title_preview}{flag_str}")
    print("-" * 80)
    print(f"Total articles: {len(articles)}   Total words: "
          f"{sum(a.word_count for a in articles):,}")
    if issues:
        print(f"WARNING: {issues} field issue(s) detected above. Review before posting.")
    print()


def clear_cache(state_path: Path) -> None:
    """Empty articles_cache so the workflow re-reads the regenerated Markdown."""
    if not state_path.exists():
        print(f"NOTE: {state_path} not found; nothing to clear.")
        return
    state = json.loads(state_path.read_text(encoding="utf-8"))
    before = len(state.get("articles_cache", []))
    state["articles_cache"] = []
    state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    print(f"Cleared articles_cache in {state_path.name} ({before} -> 0). "
          f"The workflow will re-read articles.md on the next run.")


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent

    parser = argparse.ArgumentParser(description="Convert articles.docx to articles.md")
    parser.add_argument("--input", default="data/articles.docx",
                        help="Path to the .docx file (default: data/articles.docx)")
    parser.add_argument("--output", default="data/articles.md",
                        help="Path to the output .md file (default: data/articles.md)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Parse and report only; do not write any files")
    parser.add_argument("--no-backup", action="store_true",
                        help="Overwrite the output without creating a timestamped backup")
    parser.add_argument("--clear-cache", action="store_true",
                        help="Also empty articles_cache in workflow_state.json after writing")
    parser.add_argument("--if-newer", action="store_true",
                        help="Only convert when articles.docx is newer than articles.md "
                             "(safe to call on every scheduled run)")
    args = parser.parse_args()

    docx_path = (repo_root / args.input) if not Path(args.input).is_absolute() else Path(args.input)
    md_path = (repo_root / args.output) if not Path(args.output).is_absolute() else Path(args.output)

    if not docx_path.exists():
        print(f"ERROR: Input file not found: {docx_path}")
        return 1

    # In --if-newer mode, do nothing unless the .docx has been edited since the
    # .md was last generated. This makes the converter cheap to call on every
    # scheduled run: it only does real work the week the .docx actually changes.
    if args.if_newer and md_path.exists():
        if docx_path.stat().st_mtime <= md_path.stat().st_mtime:
            print(f"Up to date: {md_path.name} is newer than or equal to "
                  f"{docx_path.name}; nothing to do.")
            return 0
        print(f"Detected updated {docx_path.name} (newer than {md_path.name}); "
              f"regenerating...")

    print(f"Reading: {docx_path}")
    try:
        articles = parse_docx(docx_path)
    except ImportError:
        print("ERROR: python-docx is not installed.")
        print("       Install it with: pip install python-docx")
        return 1

    if not articles:
        print("ERROR: No articles found. Expected 'Article #N' heading paragraphs.")
        return 1

    report(articles)

    markdown = build_markdown(articles)

    if args.dry_run:
        print("DRY RUN: no files written. Preview of first 1200 characters:")
        print("-" * 80)
        print(markdown[:1200])
        print("-" * 80)
        return 0

    # Back up existing output before overwriting
    if md_path.exists() and not args.no_backup:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = md_path.with_suffix(md_path.suffix + f".bak.{stamp}")
        backup.write_bytes(md_path.read_bytes())
        print(f"Backed up existing {md_path.name} -> {backup.name}")

    # Atomic write: render to a temp file then replace, so a crash mid-write can
    # never leave a truncated/corrupt articles.md in place.
    md_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = md_path.with_suffix(md_path.suffix + ".tmp")
    tmp_path.write_text(markdown, encoding="utf-8")
    os.replace(tmp_path, md_path)
    print(f"Wrote: {md_path}  ({len(markdown):,} bytes, {len(articles)} articles)")

    if args.clear_cache:
        clear_cache(repo_root / "workflow_state.json")
    else:
        print()
        print("NEXT STEP: clear the cached articles so the app re-reads this file:")
        print("   python scripts/clear_article_cache.py")
        print("   (or re-run this converter with --clear-cache)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
