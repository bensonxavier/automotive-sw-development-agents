import json
from pathlib import Path

import pytest

from agents.sr_analyst import analyze_requirements


FIXTURE = Path(__file__).parents[1] / "fixtures" / "sample_srs.json"


def test_analyzes_fixture_and_preserves_traceability():
	document = json.loads(FIXTURE.read_text())

	result = analyze_requirements(document)

	assert result["requirement_count"] == 3
	assert result["summary"]["functional"] == 2
	assert result["summary"]["constraint"] == 1
	assert result["requirements"][0]["id"] == "SR-LKA-001"
	assert result["requirements"][0]["source"]["source"] == "stakeholder-workshop-2026-09"


def test_flags_ambiguous_terms_and_marks_refinement_needed():
	result = analyze_requirements([{"id": "SR-1", "text": "The system shall respond quickly."}])

	codes = {finding["code"] for finding in result["requirements"][0]["findings"]}
	assert "ambiguous_term" in codes
	assert result["requirements"][0]["testability"] == "needs_refinement"


def test_detects_missing_fields_and_duplicate_ids():
	result = analyze_requirements([
		{"id": "SR-1", "text": "The system shall operate."},
		{"id": "SR-1", "description": ""},
	])

	assert result["findings"][0]["code"] == "duplicate_id"
	missing_codes = {finding["code"] for finding in result["requirements"][1]["findings"]}
	assert {"missing_text", "missing_source"}.issubset(missing_codes)


def test_rejects_invalid_input():
	with pytest.raises(TypeError):
		analyze_requirements({"requirements": "not-a-list"})
