"""
output.py — Result writer and console renderer.

write_output() serialises the RunOutput to a JSON file.
print_summary() renders a human-readable story list to stdout.

Implemented in Epic D (D4). Both functions are available immediately (Epic A)
since they only depend on the schema, not the AI pipeline.
"""

import json
from schemas import RunOutput


def write_output(result: RunOutput, path: str) -> None:
    """Write the RunOutput to a JSON file at the given path."""
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(result.to_json())


def print_summary(result: RunOutput) -> None:
    """Print a readable story summary to stdout."""
    print()
    print("=" * 60)
    print(f"  Smart Backlog Assistant — {len(result.stories)} story/stories generated")
    print("=" * 60)

    for story in result.stories:
        print(f"\n[{story.id}] {story.title}  ({story.priority})")
        print(f"  {story.description}")
        print("  Acceptance criteria:")
        for ac in story.acceptance_criteria:
            print(f"    • {ac}")
        print(f"  Category : {story.category}")
        print(f"  Source   : {story.source_reference}")

    print()
    print("Summary:")
    print(f"  {result.summary}")

    if result.warnings:
        print()
        print("Warnings:")
        for w in result.warnings:
            print(f"  ⚠  {w}")

    print()
