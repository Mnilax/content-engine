"""CLI entry point — typer-based command interface."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import anthropic
import typer
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.text import Text

from engine.formats import FORMAT_REGISTRY
from engine.sources import extract_source

app = typer.Typer(help="Social Content Engine — repurpose sources into social formats")
console = Console()


@app.command()
def make(
    url: Annotated[str, typer.Argument(help="Source URL (YouTube, article, or file path)")],
    article: Annotated[Path | None, typer.Option("--article", "-a", help="Path to your article file")] = None,
    formats: Annotated[str, typer.Option("--formats", "-f", help="Comma-separated: quote,thread,qrt,card")] = "quote",
    style: Annotated[str, typer.Option("--style", "-s", help="Style: long or short (for quote-tweet)")] = "long",
    output: Annotated[Path | None, typer.Option("--output", "-o", help="Output directory for generated files")] = None,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Show prompts without calling API")] = False,
):
    """Generate social content from a source URL + your article."""
    format_keys = list(dict.fromkeys(f.strip() for f in formats.split(",")))
    unknown = [f for f in format_keys if f not in FORMAT_REGISTRY]
    if unknown:
        raise typer.BadParameter(f"Unknown formats: {unknown}. Available: {list(FORMAT_REGISTRY)}", param_hint="--formats")
    if style not in ("long", "short"):
        raise typer.BadParameter("Style must be long or short", param_hint="--style")
    if article is not None and not article.is_file():
        raise typer.BadParameter("Article file does not exist", param_hint="--article")
    # Extract source
    console.print(f"[bold]Extracting source:[/bold] {escape(url)}")
    try:
        source = extract_source(url)
    except (OSError, ValueError) as e:
        console.print(str(e), style="red", markup=False)
        raise typer.Exit(1) from e
    console.print(f"  Title: {source.title}", markup=False)
    console.print(f"  Type: {source.source_type}")
    console.print(f"  Text length: {len(source.text)} chars")

    # Load article
    article_text = ""
    if article and article.exists():
        article_text = article.read_text(encoding="utf-8")
        console.print(f"[bold]Article loaded:[/bold] {escape(article.name)} ({len(article_text)} chars)")
    else:
        console.print("[yellow]No article provided — generating without article context[/yellow]")

    # Generate each format
    for fmt_key in format_keys:
        fmt = FORMAT_REGISTRY[fmt_key]
        console.print(f"\n[bold cyan]Generating: {fmt['name']}[/bold cyan]")

        user_prompt = fmt["build_prompt"](
            source_text=source.text,
            source_title=source.title,
            source_url=source.url,
            article_text=article_text,
            style=style,
        )

        if dry_run:
            console.print(Panel(
                Text(f"System prompt:\n{fmt['system_prompt'][:200]}...\n\n"
                     f"User prompt:\n{user_prompt[:300]}..."),
                title=f"DRY RUN: {fmt['name']}",
            ))
            continue

        # Call API
        try:
            from engine.client import generate

            result = generate(
                system_prompt=fmt["system_prompt"],
                user_prompt=user_prompt,
            )

            console.print(Panel(
                Text(result.text),
                title=f"✅ {fmt['name']}",
                border_style="green",
            ))
            console.print(
                f"  [dim]Model: {result.model} | "
                f"Tokens: {result.input_tokens}→{result.output_tokens}[/dim]"
            )

            # Save to file if output dir specified
            if output:
                output.mkdir(parents=True, exist_ok=True)
                out_file = output / f"{fmt_key}.txt"
                out_file.write_text(result.text, encoding="utf-8")
                console.print(f"  [dim]Saved to: {out_file}[/dim]")

        except (ValueError, anthropic.APIError, OSError) as e:
            console.print(f"Generation failed: {e}", style="red", markup=False)
            raise typer.Exit(1) from e


@app.command()
def formats():
    """List available output formats."""
    console.print("[bold]Available formats:[/bold]\n")
    for key, fmt in FORMAT_REGISTRY.items():
        console.print(f"  [cyan]{key}[/cyan] — {fmt['name']}")


def main():
    app()


if __name__ == "__main__":
    main()
