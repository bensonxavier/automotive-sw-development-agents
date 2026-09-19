from pathlib import Path

import pytest

from tools.parsers.markdown_requirements import RequirementParseError, parse_file, parse_markdown


FIXTURE = Path(__file__).parents[1] / "fixtures" / "sample_stakeholder_requirements.md"


def test_parses_requirements_and_preserves_traceability():
    result = parse_file(FIXTURE)

    assert result["requirement_count"] == 2
    assert result["assumptions"] == [
        "Vehicle: Passenger car, SAE Level 2 ADAS",
        "Speed range: 60–130 km/h",
        "Road type: Structured roads with visible lane markings",
    ]
    assert result["requirements"][0]["id"] == "SR-LKA-001"
    assert result["requirements"][1]["asil"] == "C"
    assert result["requirements"][1]["source_reference"]["start_line"] == 14


def test_rejects_requirement_with_missing_required_fields():
    with pytest.raises(RequirementParseError, match=r"missing required field\(s\): source"):
        parse_markdown(
            "## SR-LKA-001: Missing source\n"
            "**Category:** Functional\n"
            "**Description:** The system shall operate.\n"
            "**Rationale:** Required behavior.\n"
        )


def test_rejects_markdown_without_requirement_sections():
    with pytest.raises(RequirementParseError, match="No requirement sections"):
        parse_markdown("# Stakeholder Requirements\n")