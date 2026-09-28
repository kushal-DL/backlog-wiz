"""
ai_client.py — OpenAI-compatible Chat Completions wrapper.
All LLM calls go through generate(). Supports --mock for offline testing.
Uses streaming to avoid NVIDIA's 5-minute gateway timeout on long responses.
"""
import json
import os
import re

from openai import OpenAI, AuthenticationError, RateLimitError, APITimeoutError, APIConnectionError

# Mock response for --mock / offline pipeline tests
_MOCK = {
    "stories": [
        {
            "id": "S-001",
            "title": "Send weekly digest email",
            "description": "As a registered user, I want a weekly digest email, so that I stay informed without logging in daily.",
            "acceptance_criteria": [
                "Email sent every Monday at 08:00 UTC.",
                "Digest includes up to 10 items from the prior 7 days.",
                "One-click unsubscribe link in the footer.",
            ],
            "priority": "Should",
            "category": "feature",
            "source_reference": "weekly digest under 'engagement improvements'",
        },
        {
            "id": "S-002",
            "title": "Filter activity feed by date range",
            "description": "As a product owner, I want to filter the activity feed by date range, so that I can review sprint changes.",
            "acceptance_criteria": [
                "Date picker accepts ranges up to 90 days.",
                "Feed updates without a full page reload.",
                "Selected range is preserved on browser refresh.",
            ],
            "priority": "Must",
            "category": "feature",
            "source_reference": "sprint review filtering requirement",
        },
    ],
    "summary": "Two requirements: weekly digest email and date-range feed filtering.",
    "warnings": [],
}


def _client(model_override=None):
    key = os.environ.get("MODEL_KEY")
    if not key:
        raise EnvironmentError("MODEL_KEY not set. Copy .env.example to .env and add your key.")
    base_url = os.environ.get("MODEL_URL", "https://integrate.api.nvidia.com/v1")
    model = model_override or os.environ.get("MODEL_NAME", "nvidia/nemotron-3.5-lightning-30b-a3b")
    return OpenAI(api_key=key, base_url=base_url), model


def generate(messages: list, model_override=None, mock: bool = False) -> dict:
    """Call the LLM and return a parsed JSON dict matching the RunOutput schema."""
    if mock:
        return _MOCK

    client, model = _client(model_override)
    try:
        # stream=True avoids NVIDIA's 5-min gateway timeout; Nemotron reasons
        # extensively before outputting JSON, so the connection must stay open.
        # max_tokens=8192 gives headroom for reasoning + full JSON output.
        stream = client.chat.completions.create(
            model=model, messages=messages,
            temperature=0.2, max_tokens=8192, stream=True,
        )
        content = "".join(
            chunk.choices[0].delta.content or ""
            for chunk in stream
        )
    except AuthenticationError as e:
        raise RuntimeError(f"Auth failed — check MODEL_KEY. {e}") from e
    except RateLimitError as e:
        raise RuntimeError(f"Rate limit exceeded. {e}") from e
    except (APITimeoutError, APIConnectionError) as e:
        raise RuntimeError(f"Connection error — check MODEL_URL. {e}") from e

    return _extract_json(content)


def _extract_json(content: str) -> dict:
    """Extract the first valid JSON object that contains a 'stories' key.
    Nemotron wraps its answer in reasoning text — before AND after the JSON.
    A simple rfind('}') fails when the model adds explanatory text after the JSON.
    Balanced-brace tracking finds every complete {…} object in the response;
    we pick the rightmost one that has the expected 'stories' key.
    """
    try:
        data = json.loads(content)
        if "stories" in data:
            return data
    except json.JSONDecodeError:
        pass

    candidates = []
    for m in re.finditer(r"\{", content):
        start = m.start()
        depth, in_str, esc = 0, False, False
        for i, ch in enumerate(content[start:], start):
            if esc:
                esc = False; continue
            if ch == "\\" and in_str:
                esc = True; continue
            if ch == '"':
                in_str = not in_str; continue
            if in_str:
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        data = json.loads(content[start: i + 1])
                        if isinstance(data, dict) and "stories" in data:
                            candidates.append(data)
                    except json.JSONDecodeError:
                        pass
                    break

    if candidates:
        return candidates[-1]  # prefer the last (usually the complete, corrected one)
    raise RuntimeError(f"Could not extract valid JSON from response: {content[:200]!r}")
