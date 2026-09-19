# Approval-Gate Label Taxonomy

Defines the GitHub label scheme that drives stage transitions in the multi-team orchestrator framework. Additive to the fixture repo's existing ASIL/traceability labels — different prefixes, no collisions.

## 1. Label Categories

### `stage:*` — current lifecycle stage of a work item (set by the framework, not humans)
| Label | Meaning |
|---|---|
| `stage:requirements` | Work item is with the Requirements Orchestrator |
| `stage:design` | With the Design Orchestrator |
| `stage:architecture` | With the Architecture Orchestrator |
| `stage:implementation` | With the Implementation Orchestrator |
| `stage:test` | With the Test Orchestrator |
| `stage:done` | Merged/closed — terminal |

Exactly one `stage:*` label should be present on a work item at a time. The framework swaps it when a stage transition is consumed.

### `approved:*` — human approval signal (set by humans, consumed by the framework)
| Label | Meaning |
|---|---|
| `approved:requirements` | Human approved the Requirements draft → advance to Design |
| `approved:design` | Human approved the Design draft → advance to Architecture |
| `approved:architecture` | Human approved the Architecture draft → advance to Implementation |
| `approved:implementation` | Human approved the PR → advance to Test |
| `approved:test` | Human approved test results → merge / `stage:done` |

A human applies the `approved:<current stage>` label (or approves the PR, for implementation/test). The reconciliation poll detects it, advances `stage:*`, removes the consumed `approved:*` label, and hands the work item to the next orchestrator. This keeps `approved:*` labels always representing a *pending, unconsumed* approval — never historical record (traceability of past approvals lives in the issue/PR comment history instead).

### `changes-requested:*` — rejection signal (set by humans)
| Label | Meaning |
|---|---|
| `changes-requested:requirements` | Draft rejected; Requirements Orchestrator must redraft |
| `changes-requested:design` | Same, for Design |
| `changes-requested:architecture` | Same, for Architecture |
| `changes-requested:implementation` | Same, for Implementation |
| `changes-requested:test` | Same, for Test |

Mutually exclusive with the matching `approved:*` label for the same stage — a human applies one or the other, never both.

### `in-progress:*` — which orchestrator is actively drafting (set by the framework)
| Label | Meaning |
|---|---|
| `in-progress:requirements` / `design` / `architecture` / `implementation` / `test` | An orchestrator instance has claimed this work item and is drafting. Cleared when the draft is posted and the item is awaiting human approval. |

Lets a human glance at an issue and know "is this waiting on the agent, or waiting on me?" without opening the pipeline state store.

### `escalation:line-manager` — capability-gap flag (set by the framework)
Applied when a Line Manager agent detects a pattern worth human attention (e.g. repeated `changes-requested` on the same discipline). Not stage-blocking — informational, for the human Project Manager.

### `priority:*` — optional, PM-controlled
`priority:high` / `priority:medium` / `priority:low` — used by the Assignment Registry as a tiebreaker when the shared pool is under load.

## 2. Label Definitions File

See `labels.yml` — importable via `github-label-sync` or the GitHub CLI (`gh label create`).

## 3. Lifecycle Example

1. Issue opened → webhook workflow adds `stage:requirements`.
2. Assignment Registry claims a `RequirementsOrchestratorAgent` instance → adds `in-progress:requirements`.
3. Agent posts its draft as an issue comment, removes `in-progress:requirements`.
4. Human reviews, adds `approved:requirements`.
5. Reconciliation poll detects it → removes `approved:requirements` and `stage:requirements`, adds `stage:design`. Cycle repeats.
6. If a human instead adds `changes-requested:requirements`, the same orchestrator re-drafts; `stage:requirements` stays put.
