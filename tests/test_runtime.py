from types import SimpleNamespace

import httpx
import pytest
from typer.testing import CliRunner

from engine.cli import app
from engine.client import generate
from engine.sources import extract_source


def test_failed_fetch_stops_before_generation(monkeypatch):
    def failed_get(url, **kwargs):
        return httpx.Response(404, request=httpx.Request("GET", url), text="Not found")

    monkeypatch.setattr("engine.sources.httpx.get", failed_get)
    result = CliRunner().invoke(app, ["make", "https://example.com/missing"])
    assert result.exit_code == 1
    assert "Could not fetch source" in result.output
    assert "Generating:" not in result.output


def test_youtube_text_is_not_misclassified_as_url():
    source = extract_source("Notes on youtube.com from today's conversation")
    assert source.source_type == "paste"


def test_long_pasted_content():
    assert extract_source("Long content " * 1000).source_type == "paste"


def test_web_extraction_decodes_entities_and_removes_scripts(monkeypatch):
    html = "<title>A &amp; B</title><SCRIPT>bad()</SCRIPT><p>Useful &lt;text&gt;</p>"
    monkeypatch.setattr("engine.sources.httpx.get", lambda url, **kw: httpx.Response(
        200, request=httpx.Request("GET", url), text=html
    ))
    source = extract_source("https://example.com/youtube.com")
    assert source.source_type == "article"
    assert source.title == "A & B"
    assert "Useful <text>" in source.text
    assert "bad()" not in source.text


@pytest.mark.parametrize("args", [["-f", "unknown"], ["-s", "invalid"], ["-a", "missing.md"]])
def test_invalid_options_fail_before_source_fetch(monkeypatch, args):
    monkeypatch.setattr("engine.cli.extract_source", lambda _: pytest.fail("must validate first"))
    result = CliRunner().invoke(app, ["make", "https://example.com", *args])
    assert result.exit_code == 2


def test_missing_key_is_nonzero(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    result = CliRunner().invoke(app, ["make", "Some pasted source"])
    assert result.exit_code == 1
    assert "ANTHROPIC_API_KEY not set" in result.output


def test_pasted_brackets_are_literal_terminal_text():
    result = CliRunner().invoke(app, ["make", "[bad]source[/nonsense]", "--dry-run"])
    assert result.exit_code == 0
    assert "[bad]source[/nonsense]" in result.output


def test_generation_collects_text_blocks(monkeypatch):
    response = SimpleNamespace(
        content=[SimpleNamespace(type="thinking"), SimpleNamespace(type="text", text="one"), SimpleNamespace(type="text", text="two")],
        model="mock", usage=SimpleNamespace(input_tokens=1, output_tokens=2),
    )
    calls = []
    def create(**kwargs):
        calls.append(kwargs)
        return response
    client = SimpleNamespace(messages=SimpleNamespace(create=create))
    monkeypatch.setattr("engine.client.get_client", lambda: client)
    monkeypatch.delenv("ANTHROPIC_MODEL", raising=False)
    assert generate("system", "user").text == "one\ntwo"
    assert calls[-1]["model"] == "claude-sonnet-4-6"
    monkeypatch.setenv("ANTHROPIC_MODEL", "configured-model")
    generate("system", "user")
    assert calls[-1]["model"] == "configured-model"
    generate("system", "user", model="explicit-model")
    assert calls[-1]["model"] == "explicit-model"


def test_invalid_max_tokens(monkeypatch):
    monkeypatch.setattr("engine.client.get_client", lambda: object())
    with pytest.raises(ValueError, match="positive integer"):
        generate("system", "user", max_tokens=0)
