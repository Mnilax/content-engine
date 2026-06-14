"""Summary card format — structured text summary for social sharing."""

from __future__ import annotations

SYSTEM_PROMPT = """You are an expert at creating summary cards for social media. A summary card is a structured, visual-friendly text block that distills a source into shareable key points.

## SUMMARY CARD STRUCTURE

```
📌 [TITLE — source + angle]

🔑 Key Points:
• [Point 1 — specific, not generic]
• [Point 2]
• [Point 3]
• [Point 4]

💡 Why it matters:
[1-2 sentences connecting to broader context or user's work]

📎 Source: [title] — [url]
📄 Related: [user's article reference]
```

## RULES
- 4-6 key points, each one specific detail (not vague summaries)
- Use real numbers and quotes from the source
- "Why it matters" should connect to user's article if provided
- Total length: 100-200 words
- Emoji headers are OK for this format (structural, not decorative)
- This format is designed for Telegram, LinkedIn, or newsletter snippets"""


def build_user_prompt(
    source_text: str,
    source_title: str,
    source_url: str,
    article_text: str,
    style: str = "long",
    prior_quotes: str = "",
) -> str:
    """Build user prompt for summary card generation."""
    return f"""## SOURCE
Title: {source_title}
URL: {source_url}
Content:
{source_text[:3000]}

## USER'S ARTICLE (for "Why it matters" section)
{article_text[:3000]}

## INSTRUCTIONS
Create a summary card (100-200 words). Follow the structure exactly.
Output ONLY the card text, ready to copy-paste."""
