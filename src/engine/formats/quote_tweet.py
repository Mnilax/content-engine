"""Quote-tweet format — rules adapted from the quote-tweet-writing SKILL.

Core rules:
- Hook: [Name/role] + [recency verb] + [specific action], fits on ONE line
- Verbatim quotes: only real quotes from source or article, never invented
- Numbers: only attributable (from source or article), never invented
- Anti-duplication: no word-for-word reuse across series
- Two styles: long (Karpathy/Boris) and short (Movez)
"""

from __future__ import annotations

SYSTEM_PROMPT = """You are an expert X (Twitter) quote-tweet writer. You produce quote-tweets that link a third-party source (video, podcast, talk, article) to the user's own article.

## STRUCTURE RULES

### Hook (first line — MOST IMPORTANT)
- Formula: [Name OR role] [recency verb] [specific action] [object/context]
- Recency verbs: just opened, just shipped, just listed, just said, just dropped, ships, throws, runs
- Must fit on ONE line — use semicollon, comma, em-dash, or colon to connect. NEVER period in the hook.
- ❌ "Anthropic shipped X today" (corporate subject, no personality)
- ❌ "Check out this video" (no hook)
- ❌ "AI is changing X" (generic)
- ✓ "Boris Cherny ships 30 PRs a day from his phone"

### Style A — Long-form (150-260 words, 8-14 short paragraphs)
Use when source has framing material, audience is dev/operator, contrarian angle works.
Structure: hook → their words → their framing (> bullets) → interpretation → personal stake with numbers → verbatim from article in > block → measurement → short closer

### Style B — Short positive (40-80 words, 5-7 blocks)
Use when source is a demo/product video, broad audience, positive recommendation.
Structure: hook → trio of micro-facts → verbatim one line → pipeline with → arrows → provocation closer

### CRITICAL RULES
1. Verbatim quotes in > blocks — ONLY real quotes from source or article. Never invent.
2. Numbers — ONLY attributable (from source or article). If no real number, leave slot empty.
3. Anti-duplication — never reuse word-for-word phrases across series. Extract structure, write fresh.
4. No emojis unless user explicitly requests
5. Lowercase tone matching user's voice
6. No brand watermarks or sign-offs
7. Closer must be short, specific, inversive — different structure per quote in a series
8. Em-dashes: max 2-3 per quote"""


def build_user_prompt(
    source_text: str,
    source_title: str,
    source_url: str,
    article_text: str,
    style: str = "long",
    prior_quotes: str = "",
) -> str:
    """Build the user prompt for quote-tweet generation.

    Args:
        source_text: Extracted text from the source
        source_title: Title of the source
        source_url: URL of the source being quoted
        article_text: User's article text to link to
        style: "long" (Karpathy) or "short" (Movez)
        prior_quotes: Previous quote-tweets in the series (for anti-duplication)
    """
    style_instruction = (
        "Use Style A (long-form, 150-260 words, contrarian/operator angle)."
        if style == "long"
        else "Use Style B (short positive, 40-80 words, recommendation angle)."
    )

    dedup_block = ""
    if prior_quotes:
        dedup_block = f"""

## ANTI-DUPLICATION — Prior quotes in this series (do NOT reuse structures):
{prior_quotes}
"""

    return f"""## SOURCE being quoted
Title: {source_title}
URL: {source_url}
Content:
{source_text[:3000]}

## USER'S ARTICLE to link to
{article_text[:3000]}

## INSTRUCTIONS
{style_instruction}
Write one quote-tweet. Output ONLY the tweet text, ready to copy-paste.
{dedup_block}"""
