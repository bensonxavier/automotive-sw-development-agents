# requirements-to-userstories

Agentic pipeline: Stakeholder Requirements → Features → Jira Backlog

Orchestrates independent Worker + Reviewer agents across five stages,
with RAG-augmented context from DoorsNG, Confluence, and PDFs.

## Stages
| ID | Stage | Agents |
|----|-------|--------|
| S0 | Ingestion & RAG Prep | Ingestion, RAG Index |
| S1 | SR Analysis | SR Analyst + SR Reviewer |
| S2 | Feature Derivation | Feature Derivation + Feature Reviewer |
| S3 | Backlog Refinement | Story Writer + Backlog Reviewer |
| S4 | Gate Review | Orchestrator + Gate Review |

## Quick Start
```bash
cp config/active.yaml.example config/active.yaml
# edit config/active.yaml for your project
python scripts/run_pipeline.py --config config/active.yaml
```

## Structure
- `orchestrator/`  — stage sequencing, HITL, context compression
- `agents/`        — one folder per agent (Worker + Reviewer)
- `adapters/`      — DoorsNG, Jira, Confluence, GitHub, VectorDB, PDF
- `rag/`           — namespaces, chunkers, embedder
- `rubrics/`       — reviewer scoring rubrics (iso26262, aspice, aiag_vda, custom)
- `templates/`     — story, spec, and report templates
- `config/`        — project profiles and adapter configs
- `pipeline/`      — stage orchestration, batch routing, HITL handlers
- `tools/`         — parsers, validators, scorers
- `docs/`          — architecture, API reference, runbooks
- `tests/`         — unit, integration, fixtures
- `scripts/`       — CLI entry points
