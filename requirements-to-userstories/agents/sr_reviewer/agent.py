"""Review structured SR Analyst output without external services."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional


MEASUREMENT_PATTERN = re.compile(r"\b\d+(?:\.\d+)?\s*(?:ms|s|hz|km/h|%)\b", re.IGNORECASE)


def review_analysis(analysis: Dict[str, Any], rubric: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
	"""Score SR Analyst output and return a reviewer decision."""

	if not isinstance(analysis, dict):
		raise TypeError("analysis must be an object")
	requirements = analysis.get("requirements")
	if not isinstance(requirements, list):
		raise ValueError("analysis.requirements must be a list")

	reviewed = [_review_requirement(item) for item in requirements]
	average_score = round(sum(item["score"] for item in reviewed) / len(reviewed), 3) if reviewed else 0.0
	errors = sum(item["status"] == "reject" for item in reviewed)
	refinements = sum(item["status"] == "refine" for item in reviewed)
	status = "reject" if errors else "refine" if refinements else "pass"

	return {
		"schema_version": "1.0",
		"rubric": (rubric or {}).get("name", "custom-sr-review-v1"),
		"status": status,
		"score": average_score,
		"requirement_count": len(reviewed),
		"requirements": reviewed,
		"clarification_requests": [
			request for item in reviewed for request in item["clarification_requests"]
		],
		"summary": {
			"pass": sum(item["status"] == "pass" for item in reviewed),
			"refine": refinements,
			"reject": errors,
			"clarification_count": sum(len(item["clarification_requests"]) for item in reviewed),
		},
	}


def _review_requirement(requirement: Dict[str, Any]) -> Dict[str, Any]:
	if not isinstance(requirement, dict):
		raise ValueError("each analyzed requirement must be an object")
	requirement_id = str(requirement.get("id", "UNIDENTIFIED"))
	text = str(requirement.get("text", "")).strip()
	findings: List[Dict[str, str]] = []
	clarifications: List[Dict[str, str]] = []

	for finding in requirement.get("findings", []):
		if not isinstance(finding, dict):
			continue
		severity = str(finding.get("severity", "warning"))
		code = str(finding.get("code", "analyst_finding"))
		message = str(finding.get("message", "Analyst finding requires review."))
		findings.append({"code": code, "severity": severity, "message": message})
		if severity in {"warning", "error"}:
			clarifications.append(_clarification(requirement_id, code, message))

	if not requirement.get("acceptance_criteria"):
		findings.append({"code": "missing_acceptance_criteria", "severity": "warning", "message": "No acceptance criteria were produced."})
		clarifications.append(_clarification(requirement_id, "missing_acceptance_criteria", "Define observable acceptance criteria."))

	if _is_safety_relevant(requirement) and not MEASUREMENT_PATTERN.search(text):
		findings.append({"code": "missing_safety_measure", "severity": "warning", "message": "Safety-relevant requirement has no measurable timing, threshold, or limit."})
		clarifications.append(_clarification(requirement_id, "missing_safety_measure", "Specify the measurable safety threshold, timing, or limit and how it will be verified."))

	score = _score(requirement, findings)
	status = "reject" if any(item["severity"] == "error" for item in findings) else "refine" if findings else "pass"
	return {
		"id": requirement_id,
		"status": status,
		"score": score,
		"findings": findings,
		"clarification_requests": clarifications,
	}


def _is_safety_relevant(requirement: Dict[str, Any]) -> bool:
	source = requirement.get("source")
	if not isinstance(source, dict):
		return False
	category = str(source.get("category", "")).lower()
	return "safety" in category or bool(source.get("asil")) or bool(source.get("safety_note"))


def _score(requirement: Dict[str, Any], findings: List[Dict[str, str]]) -> float:
	score = 1.0
	for finding in findings:
		score -= 0.35 if finding["severity"] == "error" else 0.15
	if requirement.get("testability") == "needs_refinement":
		score -= 0.1
	return max(0.0, round(score, 3))


def _clarification(requirement_id: str, code: str, question: str) -> Dict[str, str]:
	return {"requirement_id": requirement_id, "code": code, "question": question}
