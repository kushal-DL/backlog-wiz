"""
prompts.py — Story-generation prompt templates.
All prompt strings live here; nothing is defined inline in other modules.
"""

# One-shot example using fictional content — the only format reference.
# Keeping a single concrete example (no separate abstract schema template)
# prevents the model from echoing the placeholder field values as output.
_EXAMPLE = """\
Correct output example:
{
  "stories": [{
    "id": "S-001",
    "title": "Export report as PDF",
    "description": "As a project manager, I want to export the weekly report as a PDF, so that I can share it with stakeholders who do not have system access.",
    "acceptance_criteria": [
      "PDF generated within 5 seconds for reports up to 50 rows.",
      "Filename includes the report date in YYYY-MM-DD format."
    ],
    "priority": "Should",
    "category": "feature",
    "source_reference": "stakeholder requested PDF export in the 14 Jan review"
  }],
  "summary": "Primary requirement is PDF export for weekly reports.",
  "warnings": []
}"""

# Appended to the conversation on validation failure to trigger a repair attempt
REPAIR_INSTRUCTION = (
    "\n\nYour previous response did not match the required JSON schema. "
    "Return only valid JSON. No text outside the JSON object."
)


def build_messages(input_text: str, backlog_context: str = "") -> list:
    """Return system + user message list for chat.completions.create."""
    return [
        {"role": "system", "content": _system()},
        {"role": "user", "content": _user(input_text, backlog_context)},
    ]


def build_repair_messages(original: list, bad_response: str) -> list:
    """Append the bad response and a repair instruction for a retry call."""
    return original + [
        {"role": "assistant", "content": bad_response},
        {"role": "user", "content": REPAIR_INSTRUCTION},
    ]


def _system() -> str:
    # Brief system message prevents the reasoning model from entering its
    # chain-of-thought mode. All task instructions are in the user message.
    return (
        "You are a JSON API. Output ONLY valid JSON. "
        "No reasoning, no explanation, no prose. "
        "Your response must start with '{' and end with '}'."
    )


def _user(input_text: str, backlog_context: str) -> str:
    parts = [
        "Extract user stories from the input text below and return them as JSON.\n\n"
        "Each story must have these fields: id (S-001, S-002, …), title (short imperative "
        "phrase), description (exactly: 'As a <persona>, I want <goal>, so that <benefit>'), "
        "acceptance_criteria (list of at least 2 testable criteria), "
        "priority (one of: Must / Should / Could / Won't), "
        "category (one of: feature / infrastructure / testing / documentation), "
        "source_reference (brief quote from the input).\n"
        "Top-level keys: stories (flat array), summary (2-3 sentences), warnings (overlaps with existing backlog).\n"
        "Do not invent requirements. Do not nest arrays inside stories.\n\n"
        f"{_EXAMPLE}\n\n"
        f"Input text:\n\n{input_text}"
    ]
    if backlog_context:
        parts.append(
            "Existing backlog items — flag duplicates in warnings[], do not drop them:\n\n"
            + backlog_context
        )
    return "\n\n---\n\n".join(parts)

