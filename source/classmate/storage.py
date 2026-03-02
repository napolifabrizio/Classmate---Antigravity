"""
storage.py
----------
Saves the meeting transcript and review to the `data/` folder.
"""

from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path

# Project root is three levels up from this file:
# source/classmate/storage.py  →  project root
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_DATA_DIR = _PROJECT_ROOT / "data"


def save(
    transcript: str,
    review: dict,
    audio_path: str,
) -> tuple[Path, Path]:
    """
    Write *transcript* and *review* to `data/` with a timestamp prefix.

    Files created
    -------------
    data/<timestamp>_transcript.txt  — plain-text transcript
    data/<timestamp>_review.md       — Markdown-formatted review

    Parameters
    ----------
    transcript : str
        Full meeting transcript text.
    review : dict
        Structured review dict from reviewer.review().
    audio_path : str
        Original audio file path (stored as metadata in the review file).

    Returns
    -------
    tuple[Path, Path]
        (transcript_path, review_path)
    """
    _DATA_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    audio_name = Path(audio_path).stem

    # --- Transcript file ---
    transcript_path = _DATA_DIR / f"{timestamp}_{audio_name}_transcript.txt"
    transcript_path.write_text(transcript, encoding="utf-8")

    # --- Review file (Markdown) ---
    review_path = _DATA_DIR / f"{timestamp}_{audio_name}_review.md"
    key_points_md = "\n".join(f"- {p}" for p in review.get("key_points", []))
    action_items_md = "\n".join(f"- [ ] {a}" for a in review.get("action_items", []))
    if not action_items_md:
        action_items_md = "_No action items identified._"

    review_md = f"""\
# Meeting Review — {timestamp}

**Source file:** `{audio_path}`

---

## Summary

{review.get("summary", "")}

---

## Key Points

{key_points_md}

---

## Action Items

{action_items_md}
"""
    review_path.write_text(review_md, encoding="utf-8")

    return transcript_path, review_path
