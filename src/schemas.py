"""
schemas.py — Output data contract. Single source of truth for story shape.
All modules import from here; never define story structure inline elsewhere.
"""
import json
from dataclasses import dataclass, field, asdict
from typing import List


@dataclass
class Story:
    id: str
    title: str
    description: str           # "As a <persona>, I want <goal>, so that <benefit>"
    acceptance_criteria: List[str]
    priority: str              # Must | Should | Could | Won't
    category: str
    source_reference: str

    VALID_PRIORITIES = {"Must", "Should", "Could", "Won't"}

    def validate(self) -> List[str]:
        """Return validation errors; empty list = valid."""
        errors = []
        if not self.title:
            errors.append(f"{self.id}: title is empty")
        if not self.description.startswith("As a"):
            errors.append(f"{self.id}: description must follow 'As a / I want / So that'")
        if not self.acceptance_criteria:
            errors.append(f"{self.id}: acceptance_criteria is empty")
        if self.priority not in self.VALID_PRIORITIES:
            errors.append(f"{self.id}: invalid priority '{self.priority}'")
        return errors


@dataclass
class RunOutput:
    stories: List[Story]
    summary: str
    warnings: List[str] = field(default_factory=list)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(asdict(self), indent=indent)

    @classmethod
    def from_dict(cls, data: dict) -> "RunOutput":
        """Deserialise AI response dict. Skips non-dict story entries with a warning."""
        raw_stories = data.get("stories", [])
        stories, warnings = [], list(data.get("warnings", []))
        for i, s in enumerate(raw_stories):
            if not isinstance(s, dict):
                # Some models wrap each story in an extra array — skip and warn
                warnings.append(f"Story at index {i} was not a JSON object; skipped.")
                continue
            stories.append(Story(**s))
        return cls(stories=stories, summary=data.get("summary", ""), warnings=warnings)

    def all_validation_errors(self) -> List[str]:
        errors = []
        for story in self.stories:
            errors.extend(story.validate())
        return errors
