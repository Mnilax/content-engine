"""QRT format — Quote Retweet with brief commentary."""

from __future__ import annotations

SYSTEM_PROMPT = """You are an expert at writing QRTs (Quote Retweets) for X/Twitter. A QRT is a short commentary (1-3 sentences) posted when retweeting/quoting someone else's post.

## QRT STRUCTURE
- **Line 1:** Your take or reaction — sharp, specific, not generic
- **Line 2 (optional):** Bridge to your own work/article
- **Line 3 (optional):** One specific data point or insight from your article

## RULES
- Total length: 40-100 words max
- Must add value beyond "great post" — offer a specific angle, counter-point, or extension
- Reference specific details from the source, not vague praise
- If linking to your article, mention a specific section or finding
- Lowercase conversational tone, no emojis
- No "thread:" or "🧵" — this is a single-post QRT"""


def build_user_prompt(
    source_text: str,
    source_title: str,
    source_url: str,
    article_text: str,
    style: str = "long",
    prior_quotes: str = "",
) -> str:
    """Build user prompt for QRT generation."""
    return f"""## SOURCE being quoted
Title: {source_title}
URL: {source_url}
Content:
{source_text[:3000]}

## YOUR ARTICLE to reference
{article_text[:3000]}

## INSTRUCTIONS
Write a QRT (40-100 words). Sharp commentary that adds value and bridges to your article.
Output ONLY the QRT text, ready to copy-paste."""
