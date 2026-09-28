"""
context.py — Existing backlog loader.
Reads backlog.json and returns a plain-text title list for prompt injection.
Keeps context window lean — titles only, not full story objects.
"""
import json
import sys
from pathlib import Path


def load_backlog_context(path: str) -> str:
    """Load backlog.json and return a numbered list of story titles.
    Returns empty string if file is absent (non-fatal — proceeds without context).
    Raises ValueError on malformed JSON.
    """
    if not path:
        return ""
    p = Path(path)
    if not p.exists():
        print(f"Warning: backlog '{path}' not found. Proceeding without context.", file=sys.stderr)
        return ""
    try:
        items = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"Backlog '{path}' contains invalid JSON: {e}") from e
    if not isinstance(items, list):
        raise ValueError(f"Backlog '{path}' must be a JSON array, got {type(items).__name__}.")
    return "\n".join(
        f"{i}. {item.get('title') or item.get('id') or f'item {i}'}"
        for i, item in enumerate(items, 1)
    )
