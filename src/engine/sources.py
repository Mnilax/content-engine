"""Source content extraction — fetch text from URLs or local files."""

from __future__ import annotations

import re
from dataclasses import dataclass
from html import unescape
from pathlib import Path
from urllib.parse import urlparse

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
    parsed = urlparse(url_or_path)
    if parsed.scheme in ("http", "https"):
        hostname = (parsed.hostname or "").lower()
        if hostname in ("youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"):
            return _from_youtube(url_or_path)
        return _from_web(url_or_path)
    try:
        is_file = Path(url_or_path).is_file()
    except OSError:
        is_file = False
    if is_file:
        return _from_file(url_or_path)
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
        resp.raise_for_status()
        html = resp.text

        # Extract title
        title_match = re.search(r"<title>(.*?)</title>", html)
        title = unescape(title_match.group(1)).replace(" - YouTube", "").strip() if title_match else "YouTube Video"

        # Extract description from meta tag
        desc_match = re.search(
            r'<meta\s+name="description"\s+content="(.*?)"', html
        )
        description = unescape(desc_match.group(1)) if desc_match else ""

        return SourceContent(
            title=title,
            text=f"Title: {title}\n\nDescription: {description}",
            url=url,
            source_type="youtube",
        )
    except httpx.HTTPError as e:
        raise ValueError(f"Could not fetch source: {url}") from e


def _from_web(url: str) -> SourceContent:
    """Fetch and extract text from a web page."""
    try:
        resp = httpx.get(
            url,
            follow_redirects=True,
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0 (content-engine)"},
        )
        resp.raise_for_status()
        html = resp.text

        # Extract title
        title_match = re.search(r"<title>(.*?)</title>", html)
        title = unescape(title_match.group(1)).strip() if title_match else url

        # Strip HTML tags for rough text extraction
        text = re.sub(r"<script\b.*?</script\s*>", "", html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<style\b.*?</style\s*>", "", text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", unescape(text)).strip()
        if not text:
            raise ValueError(f"Source has no extractable text: {url}")

        # Truncate to reasonable length
        if len(text) > 5000:
            text = text[:5000] + "..."

        return SourceContent(
            title=title,
            text=text,
            url=url,
            source_type="article",
        )
    except httpx.HTTPError as e:
        raise ValueError(f"Could not fetch source: {url}") from e
