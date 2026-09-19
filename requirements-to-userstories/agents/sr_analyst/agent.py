"""Deterministic stakeholder-requirement analysis.

The first implementation deliberately has no model or service dependency. It
normalizes common requirement JSON shapes and produces structured findings that
can later be passed to an LLM-backed analyst or reviewer.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Dict, Iterable, List


VAGUE_TERMS = {
	"appropriate",
	"efficient",
	"fast",
	"quickly",
	"reasonable",
	"robust",
	"seamless",
	" user-friendly",
	"as needed",
	"etc.",
}

FUNCTIONAL_MARKERS = ("shall", "must", "provide", "support", "allow", "enable")
NON_FUNCTIONAL_MARKERS = (
	"performance",
	"latency",
	"availability",
	"reliability",
	"security",
	"response time",
	"within ",
)
CONSTRAINT_MARKERS = ("only ", "cannot", "must not", "comply", "constraint", "shall use")


def analyze_requirements(document: Any) -> Dict[str, Any]:
	"""Analyze a requirement document and return reviewer-ready JSON.

	Accepted input is either a list of requirement objects or a mapping with a
	``requirements`` list. Each requirement should contain ``id`` and either
	``text`` or ``description``. Unknown fields are retained in ``source``.
	"""

	requirements = _extract_requirements(document)
	analyses = [_analyze_one(requirement, index) for index, requirement in enumerate(requirements, 1)]
	analyses.extend(_duplicate_findings(analyses))

	return {
		"schema_version": "1.0",
		"requirement_count": len(requirements),
		"requirements": analyses[: len(requirements)],
		"findings": analyses[len(requirements) :],
		"summary": _summary(analyses[: len(requirements)]),
	}


def _extract_requirements(document: Any) -> List[Dict[str, Any]]:
	if isinstance(document, list):
		items = document
	elif isinstance(document, dict):
		items = document.get("requirements", document.get("items", []))
	else:
		raise TypeError("document must be a list or mapping containing requirements")

	if not isinstance(items, list):
		raise TypeError("requirements must be a list")
	if not all(isinstance(item, dict) for item in items):
		raise TypeError("each requirement must be an object")
	return items


def _analyze_one(requirement: Dict[str, Any], index: int) -> Dict[str, Any]:
	requirement_id = str(requirement.get("id") or requirement.get("requirement_id") or f"UNIDENTIFIED-{index}")
	text = str(requirement.get("text") or requirement.get("description") or "").strip()
	lowered = text.lower()
	findings: List[Dict[str, str]] = []

	if not text:
		findings.append({"code": "missing_text", "severity": "error", "message": "Requirement has no text."})
	if not requirement.get("id") and not requirement.get("requirement_id"):
		findings.append({"code": "missing_id", "severity": "warning", "message": "Requirement has no stable identifier."})
	if not requirement.get("source"):
		findings.append({"code": "missing_source", "severity": "warning", "message": "Requirement has no source reference."})
	for term in VAGUE_TERMS:
		if term.strip() in lowered:
			findings.append({"code": "ambiguous_term", "severity": "warning", "message": f"Vague term: {term.strip()}"})
	if text and not any(marker in lowered for marker in ("shall", "must", "should", "is ", "are ")):
		findings.append({"code": "weak_statement", "severity": "warning", "message": "Requirement lacks a normative or observable statement."})

	return {
		"id": requirement_id,
		"text": text,
		"category": _classify(lowered),
		"testability": "needs_refinement" if findings else "testable_candidate",
		"acceptance_criteria": _acceptance_criteria(text),
		"findings": findings,
		"source": requirement,
	}


def _classify(text: str) -> str:
	if any(marker in text for marker in CONSTRAINT_MARKERS):
		return "constraint"
	if any(marker in text for marker in NON_FUNCTIONAL_MARKERS):
		return "non_functional"
	if any(marker in text for marker in FUNCTIONAL_MARKERS):
		return "functional"
	return "unclear"


def _acceptance_criteria(text: str) -> List[str]:
	if not text:
		return []
	return [f"Verify that: {text}"]


def _duplicate_findings(analyses: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
	counts = Counter(item["id"] for item in analyses)
	return [
		{
			"code": "duplicate_id",
			"severity": "error",
			"message": f"Requirement identifier '{requirement_id}' occurs {count} times.",
			"requirement_ids": [requirement_id],
		}
		for requirement_id, count in counts.items()
		if count > 1
	]


def _summary(analyses: Iterable[Dict[str, Any]]) -> Dict[str, int]:
	items = list(analyses)
	return {
		"functional": sum(item["category"] == "functional" for item in items),
		"non_functional": sum(item["category"] == "non_functional" for item in items),
		"constraint": sum(item["category"] == "constraint" for item in items),
		"unclear": sum(item["category"] == "unclear" for item in items),
		"needs_refinement": sum(item["testability"] == "needs_refinement" for item in items),
	}
