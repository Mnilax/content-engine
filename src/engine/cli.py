"""CLI entry point — typer-based command interface."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from engine.sources import extract_source
from engine.formats import FORMAT_REGISTRY

app = typer.Typer(help="Social Content Engine — repurpose sources into social formats")
console = Console()


@app.command()
def make(
    url: str = typer.Argument(help="Source URL (YouTube, article, or file path)"),
    article: Path = typer.Option(None, "--article", "-a", help="Path to your article file"),
    formats: str = typer.Option("quote", "--formats", "-f", help="Comma-separated: quote,thread,qrt,card"),
    style: str = typer.Option("long", "--style", "-s", help="Style: long or short (for quote-tweet)"),
    output: Path = typer.Option(None, "--output", "-o", help="Output directory for generated files"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show prompts without calling API"),
):
    """Generate social content from a source URL + your article."""
    # Extract source
    console.print(f"[bold]Extracting source:[/bold] {url}")
    source = extract_source(url)
    console.print(f"  Title: {source.title}")
    console.print(f"  Type: {source.source_type}")
    console.print(f"  Text length: {len(source.text)} chars")

    # Load article
    article_text = ""
    if article and article.exists():
        article_text = article.read_text(encoding="utf-8")
        console.print(f"[bold]Article loaded:[/bold] {article.name} ({len(article_text)} chars)")
    else:
        console.print("[yellow]No article provided — generating without article context[/yellow]")

    # Parse requested formats
    format_keys = [f.strip() for f in formats.split(",")]
    unknown = [f for f in format_keys if f not in FORMAT_REGISTRY]
    if unknown:
        console.print(f"[red]Unknown formats: {unknown}[/red]")
        console.print(f"Available: {list(FORMAT_REGISTRY.keys())}")
        raise typer.Exit(1)

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
                f"[dim]System prompt:[/dim]\n{fmt['system_prompt'][:200]}...\n\n"
                f"[dim]User prompt:[/dim]\n{user_prompt[:300]}...",
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
                result.text,
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

        except ValueError as e:
            console.print(f"[red]API Error: {e}[/red]")
            console.print("[yellow]Set ANTHROPIC_API_KEY in .env to generate content[/yellow]")


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
