"""Parse stakeholder requirements written in the project Markdown format."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional


REQUIREMENT_HEADING = re.compile(r"^##\s+(?P<id>SR-[A-Za-z0-9-]+):\s+(?P<title>.+?)\s*$")
FIELD_LINE = re.compile(
    r"^\*\*(?P<field>[A-Za-z][A-Za-z ]+?)(?::\*\*|\*\*:|:)\s*(?P<value>.+?)\s*$"
)
TOP_LEVEL_HEADING = re.compile(r"^##\s+(?P<title>.+?)\s*$")

FIELD_NAMES = {
    "category": "category",
    "description": "description",
    "rationale": "rationale",
    "source": "source",
    "asil": "asil",
    "safety note": "safety_note",
}


class RequirementParseError(ValueError):
    """Raised when stakeholder Markdown cannot produce a valid requirement."""


def parse_markdown(text: str, source: str = "<string>") -> Dict[str, Any]:
    """Parse stakeholder requirements into the SR Analyst input contract."""

    lines = text.splitlines()
    assumptions = _parse_assumptions(lines)
    requirements: List[Dict[str, Any]] = []
    sections = list(_requirement_sections(lines))

    if not sections:
        raise RequirementParseError(f"No requirement sections found in {source}.")

    for position, (start, match, end) in enumerate(sections):
        fields = _parse_fields(lines[start + 1 : end])
        requirement = {
            "id": match.group("id"),
            "title": match.group("title"),
            "source": fields.get("source"),
            "source_reference": {
                "document": source,
                "section": f"{match.group('id')}: {match.group('title')}",
                "start_line": start + 1,
                "end_line": end,
            },
            "category": fields.get("category"),
            "description": fields.get("description"),
            "rationale": fields.get("rationale"),
            "asil": fields.get("asil"),
            "safety_note": fields.get("safety_note"),
        }
        missing = [
            name for name in ("category", "description", "rationale", "source")
            if not requirement.get(name)
        ]
        if missing:
            raise RequirementParseError(
                f"{requirement['id']} is missing required field(s): {', '.join(missing)}."
            )
        requirements.append(requirement)

    return {
        "schema_version": "1.0",
        "source": source,
        "assumptions": assumptions,
        "requirement_count": len(requirements),
        "requirements": requirements,
    }


def parse_file(path: Path) -> Dict[str, Any]:
    """Parse a UTF-8 stakeholder Markdown file."""

    return parse_markdown(path.read_text(encoding="utf-8"), str(path))


def _requirement_sections(lines: List[str]):
    matches = []
    for index, line in enumerate(lines):
        match = REQUIREMENT_HEADING.match(line)
        if match:
            matches.append((index, match, len(lines)))
    return [
        (start, match, matches[position + 1][0] if position + 1 < len(matches) else end)
        for position, (start, match, end) in enumerate(matches)
    ]


def _parse_fields(lines: List[str]) -> Dict[str, str]:
    fields: Dict[str, str] = {}
    current: Optional[str] = None
    for line in lines:
        match = FIELD_LINE.match(line.strip())
        if match:
            field = FIELD_NAMES.get(match.group("field").lower())
            if field:
                fields[field] = match.group("value").strip()
                current = field
            else:
                current = None
            continue
        if current and line.strip() and not line.startswith("#"):
            fields[current] = f"{fields[current]} {line.strip()}".strip()
    return fields


def _parse_assumptions(lines: List[str]) -> List[str]:
    assumptions: List[str] = []
    in_assumptions = False
    for line in lines:
        heading = TOP_LEVEL_HEADING.match(line)
        if heading:
            in_assumptions = heading.group("title").lower().startswith("assumptions")
            continue
        if in_assumptions and line.strip().startswith("-"):
            assumptions.append(line.strip()[1:].strip())
    return assumptions