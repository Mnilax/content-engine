"""Source content extraction — fetch text from URLs or local files."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import httpx


@dataclass
class SourceContent:
    """Extracted source content."""

    title: str
    text: str
    url: str
    source_type: str  # "article", "youtube", "paste"


def extract_source(url_or_path: str) -> SourceContent:
    """Extract content from a URL or local file.

    Supports:
    - YouTube URLs → fetches page, extracts title + description
    - Web URLs → fetches page, extracts text
    - Local file paths → reads file content

    Args:
        url_or_path: URL or file path

    Returns:
        SourceContent with extracted text
    """
    if Path(url_or_path).exists():
        return _from_file(url_or_path)
    elif "youtube.com" in url_or_path or "youtu.be" in url_or_path:
        return _from_youtube(url_or_path)
    elif url_or_path.startswith("http"):
        return _from_web(url_or_path)
    else:
        # Treat as pasted text
        return SourceContent(
            title="Pasted content",
            text=url_or_path,
            url="",
            source_type="paste",
        )


def _from_file(path: str) -> SourceContent:
    """Read content from a local file."""
    content = Path(path).read_text(encoding="utf-8")
    return SourceContent(
        title=Path(path).stem,
        text=content,
        url=path,
        source_type="paste",
    )


def _from_youtube(url: str) -> SourceContent:
    """Extract YouTube video info from page HTML."""
    try:
        resp = httpx.get(url, follow_redirects=True, timeout=15)
        html = resp.text

        # Extract title
        title_match = re.search(r"<title>(.*?)</title>", html)
        title = title_match.group(1).replace(" - YouTube", "").strip() if title_match else "YouTube Video"

        # Extract description from meta tag
        desc_match = re.search(
            r'<meta\s+name="description"\s+content="(.*?)"', html
        )
        description = desc_match.group(1) if desc_match else ""

        return SourceContent(
            title=title,
            text=f"Title: {title}\n\nDescription: {description}",
            url=url,
            source_type="youtube",
        )
    except Exception as e:
        return SourceContent(
            title="YouTube Video",
            text=f"[Could not fetch: {e}]",
            url=url,
            source_type="youtube",
        )


def _from_web(url: str) -> SourceContent:
    """Fetch and extract text from a web page."""
    try:
        resp = httpx.get(
            url,
            follow_redirects=True,
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0 (content-engine)"},
        )
        html = resp.text

        # Extract title
        title_match = re.search(r"<title>(.*?)</title>", html)
        title = title_match.group(1).strip() if title_match else url

        # Strip HTML tags for rough text extraction
        text = re.sub(r"<script.*?</script>", "", html, flags=re.DOTALL)
        text = re.sub(r"<style.*?</style>", "", text, flags=re.DOTALL)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        # Truncate to reasonable length
        if len(text) > 5000:
            text = text[:5000] + "..."

        return SourceContent(
            title=title,
            text=text,
            url=url,
            source_type="article",
        )
    except Exception as e:
        return SourceContent(
            title=url,
            text=f"[Could not fetch: {e}]",
            url=url,
            source_type="article",
        )
