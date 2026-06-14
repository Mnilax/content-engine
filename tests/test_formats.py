"""Tests for format prompt builders and source extraction."""

from engine.sources import extract_source, SourceContent
from engine.formats.quote_tweet import build_user_prompt as qt_prompt, SYSTEM_PROMPT as QT_SYS
from engine.formats.thread import build_user_prompt as th_prompt
from engine.formats.qrt import build_user_prompt as qrt_prompt
from engine.formats.summary_card import build_user_prompt as card_prompt
from engine.formats import FORMAT_REGISTRY


def test_source_from_file(tmp_path):
    f = tmp_path / "test.md"
    f.write_text("Hello world content")
    source = extract_source(str(f))
    assert source.source_type == "paste"
    assert "Hello world" in source.text


def test_source_paste():
    source = extract_source("Some raw pasted text about AI")
    assert source.source_type == "paste"
    assert "AI" in source.text


def test_quote_tweet_prompt_structure():
    prompt = qt_prompt(
        source_text="Speaker said X about Y",
        source_title="Great Talk",
        source_url="https://example.com/talk",
        article_text="My article about templates",
        style="long",
    )
    assert "SOURCE being quoted" in prompt
    assert "Great Talk" in prompt
    assert "Style A" in prompt


def test_quote_tweet_short_style():
    prompt = qt_prompt(
        source_text="Demo content",
        source_title="Demo",
        source_url="https://example.com",
        article_text="Article",
        style="short",
    )
    assert "Style B" in prompt


def test_quote_tweet_anti_duplication():
    prompt = qt_prompt(
        source_text="Content",
        source_title="Title",
        source_url="https://example.com",
        article_text="Article",
        prior_quotes="Previous quote: the bottleneck isn't the model",
    )
    assert "ANTI-DUPLICATION" in prompt
    assert "bottleneck" in prompt


def test_thread_prompt():
    prompt = th_prompt(
        source_text="Source",
        source_title="Title",
        source_url="https://example.com",
        article_text="Article",
    )
    assert "SOURCE" in prompt
    assert "thread" in prompt.lower()


def test_qrt_prompt():
    prompt = qrt_prompt(
        source_text="Source",
        source_title="Title",
        source_url="https://example.com",
        article_text="Article",
    )
    assert "QRT" in prompt


def test_summary_card_prompt():
    prompt = card_prompt(
        source_text="Source",
        source_title="Title",
        source_url="https://example.com",
        article_text="Article",
    )
    assert "summary card" in prompt.lower()


def test_format_registry():
    assert "quote" in FORMAT_REGISTRY
    assert "thread" in FORMAT_REGISTRY
    assert "qrt" in FORMAT_REGISTRY
    assert "card" in FORMAT_REGISTRY
    for key, fmt in FORMAT_REGISTRY.items():
        assert "system_prompt" in fmt
        assert "build_prompt" in fmt
        assert callable(fmt["build_prompt"])


def test_system_prompt_has_key_rules():
    """Verify quote-tweet system prompt embeds the critical skill rules."""
    assert "recency verb" in QT_SYS.lower()
    assert "never invent" in QT_SYS.lower()
    assert "anti-duplication" in QT_SYS.lower()
    assert "hook" in QT_SYS.lower()
