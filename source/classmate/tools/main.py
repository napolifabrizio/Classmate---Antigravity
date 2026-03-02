"""
main.py
-------
CLI entry point for ClassmatePlus.

Modes:
    Record mode  (no arguments) — records from your microphone, press Enter to stop.
    File mode    (audio path)   — processes an existing audio file.

Usage:
    poetry run python source/classmate/tools/main.py            # record from mic
    poetry run python source/classmate/tools/main.py audio.mp3  # use existing file
"""

from __future__ import annotations
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Load environment variables (.env at project root) BEFORE importing openai
# ---------------------------------------------------------------------------
from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(_PROJECT_ROOT / ".env")

# ---------------------------------------------------------------------------
# Project imports
# ---------------------------------------------------------------------------
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.rule import Rule

from classmate.transcriber import transcribe
from classmate.reviewer import review
from classmate.storage import save
from classmate.recorder import record_meeting


console = Console()


def run_pipeline(audio_path: str, delete_after: bool = False) -> None:
    """Transcribe → review → save pipeline for a given audio file."""
    client = OpenAI()

    # ── 1. Transcribe ──────────────────────────────────────────────────────
    console.rule("[bold cyan]Step 1 — Transcribing audio[/]")
    console.print(f"[dim]File:[/] [yellow]{audio_path}[/]")

    with console.status("[cyan]Sending audio to Whisper…[/]", spinner="dots"):
        transcript = transcribe(audio_path, client=client)

    console.print(Panel(transcript, title="[bold]Transcript[/]", border_style="cyan"))

    # ── 2. Generate review ─────────────────────────────────────────────────
    console.rule("[bold magenta]Step 2 — Generating review[/]")

    with console.status("[magenta]Analysing with GPT-4o…[/]", spinner="dots"):
        meeting_review = review(transcript, client=client)

    summary = meeting_review.get("summary", "")
    key_points = meeting_review.get("key_points", [])
    action_items = meeting_review.get("action_items", [])

    md_text = f"## Summary\n{summary}\n\n## Key Points\n"
    md_text += "\n".join(f"- {p}" for p in key_points)
    md_text += "\n\n## Action Items\n"
    if action_items:
        md_text += "\n".join(f"- [ ] {a}" for a in action_items)
    else:
        md_text += "_No action items identified._"

    console.print(Panel(Markdown(md_text), title="[bold]Review[/]", border_style="magenta"))

    # ── 3. Save to disk ────────────────────────────────────────────────────
    console.rule("[bold green]Step 3 — Saving files[/]")

    transcript_path, review_path = save(transcript, meeting_review, audio_path)

    console.print(f"[green]✓[/] Transcript → [bold]{transcript_path}[/]")
    console.print(f"[green]✓[/] Review     → [bold]{review_path}[/]")
    console.rule("[bold green]Done![/]")

    # Clean up temp file if this was a recording
    if delete_after:
        try:
            os.remove(audio_path)
        except OSError:
            pass


def main() -> None:
    if len(sys.argv) >= 2:
        # ── File mode ──────────────────────────────────────────────────────
        audio_path = sys.argv[1]
        run_pipeline(audio_path, delete_after=False)
    else:
        # ── Record mode ────────────────────────────────────────────────────
        console.rule("[bold yellow]ClassmatePlus — Meeting Recorder[/]")
        console.print(
            "[bold]Your microphone is now recording.[/]\n"
            "Speak freely — have your meeting.\n"
            "When you're done, press [bold green]Enter[/] to stop and process.\n"
        )

        with console.status("[yellow]Recording…[/]", spinner="dots"):
            audio_path = record_meeting()

        console.print("[green]✓[/] Recording stopped.\n")
        run_pipeline(audio_path, delete_after=True)


if __name__ == "__main__":
    main()
