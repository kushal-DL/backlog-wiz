"""
validate.py — Schema validator with one bounded repair retry.
On failure, appends a repair instruction and retries once via ai_client.
Second failure raises ValueError — main.py handles the exit.
"""
import json
import logging

from schemas import RunOutput
from prompts import build_repair_messages

log = logging.getLogger(__name__)


def validate_and_repair(raw: dict, messages: list, mock: bool = False) -> RunOutput:
    """Validate raw AI response; retry once with a repair prompt on failure."""
    if mock:
        return RunOutput.from_dict(raw)  # mock response is always valid

    result, errors = _try(raw)
    if result:
        return result

    log.warning("Validation failed (%d error(s)): %s", len(errors), "; ".join(errors))
    log.info("Retrying with repair instruction...")

    from ai_client import generate  # late import avoids circular dependency
    try:
        raw_retry = generate(build_repair_messages(messages, json.dumps(raw)))
    except RuntimeError as e:
        raise ValueError(f"Repair attempt failed: {e}") from e

    result_retry, errors_retry = _try(raw_retry)
    if result_retry:
        return result_retry
    raise ValueError(f"Validation failed after retry: {'; '.join(errors_retry)}")


def _try(raw: dict):
    """Attempt deserialisation + validation. Returns (RunOutput, []) or (None, [errors])."""
    try:
        result = RunOutput.from_dict(raw)
    except (KeyError, TypeError) as e:
        return None, [f"Deserialisation failed: {e}"]
    errors = result.all_validation_errors()
    return (result, []) if not errors else (None, errors)
