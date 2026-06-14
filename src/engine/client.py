"""Anthropic API client wrapper."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class GenerationResult:
    """Result of a generation call."""

    text: str
    model: str
    input_tokens: int
    output_tokens: int


def get_client():
    """Get an Anthropic client. Raises if key not set."""
    import anthropic

    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key or api_key.startswith("sk-ant-your"):
        raise ValueError(
            "ANTHROPIC_API_KEY not set. Copy .env.example to .env and add your key."
        )
    return anthropic.Anthropic(api_key=api_key)


def generate(
    system_prompt: str,
    user_prompt: str,
    model: str | None = None,
    max_tokens: int | None = None,
) -> GenerationResult:
    """Generate text using the Anthropic API.

    Args:
        system_prompt: System instruction for the model
        user_prompt: User message with source + article content
        model: Override model name
        max_tokens: Override max tokens

    Returns:
        GenerationResult with generated text and usage stats
    """
    client = get_client()

    _model = model or os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
    _max_tokens = max_tokens or int(os.getenv("MAX_TOKENS", "2048"))

    response = client.messages.create(
        model=_model,
        max_tokens=_max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    return GenerationResult(
        text=response.content[0].text,
        model=response.model,
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
    )
