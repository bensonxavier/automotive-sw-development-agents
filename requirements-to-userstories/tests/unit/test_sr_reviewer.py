from agents.sr_reviewer import review_analysis


def _analysis(*requirements):
	return {"schema_version": "1.0", "requirements": list(requirements)}


def test_passes_clean_requirement():
	result = review_analysis(_analysis({
		"id": "SR-1",
		"text": "The system shall detect a lane boundary within 200 ms.",
		"testability": "testable_candidate",
		"acceptance_criteria": ["Verify detection within 200 ms."],
		"findings": [],
		"source": {"source": "systems-engineer", "category": "Functional"},
	}))

	assert result["status"] == "pass"
	assert result["summary"] == {"pass": 1, "refine": 0, "reject": 0, "clarification_count": 0}


def test_refines_ambiguous_requirement_with_clarification():
	result = review_analysis(_analysis({
		"id": "SR-2",
		"text": "The system shall respond quickly.",
		"testability": "needs_refinement",
		"acceptance_criteria": ["Verify that the system shall respond quickly."],
		"findings": [{"code": "ambiguous_term", "severity": "warning", "message": "Vague term: quickly"}],
		"source": {"source": "stakeholder", "category": "Functional"},
	}))

	assert result["status"] == "refine"
	assert result["clarification_requests"][0]["requirement_id"] == "SR-2"


def test_rejects_error_and_flags_safety_measure():
	result = review_analysis(_analysis({
		"id": "SR-3",
		"text": "The system shall provide safe behavior.",
		"testability": "needs_refinement",
		"acceptance_criteria": [],
		"findings": [{"code": "missing_text", "severity": "error", "message": "Requirement has no text."}],
		"source": {"source": "safety-engineer", "category": "Safety", "asil": "C"},
	}))

	codes = {finding["code"] for finding in result["requirements"][0]["findings"]}
	assert result["status"] == "reject"
	assert {"missing_text", "missing_acceptance_criteria", "missing_safety_measure"}.issubset(codes)


def test_rejects_invalid_analysis_shape():
	try:
		review_analysis({"requirements": "invalid"})
	except ValueError as error:
		assert "analysis.requirements must be a list" in str(error)
	else:
		assert False, "Expected invalid analysis shape to raise ValueError"