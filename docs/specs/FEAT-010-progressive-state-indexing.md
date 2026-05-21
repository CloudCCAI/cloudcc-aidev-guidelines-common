---
kind: feature-spec
feature_id: FEAT-010
title: Progressive state indexing
status: implemented
owner_role: shared
task_ids: TASK-010
related_decisions: ADR-010
related_issues: none
updated_at: 2026-05-21T07:05:27Z
updated_by: codex
---

# FEAT-010 - Progressive state indexing

## Requirement

As projects grow, the skill must keep hot files small and make state loading progressive. `current-status.md` should stay a hot index, `task-board.md` should stay a compact task directory, and each task should keep its own current state in `.claw/tasks/TASK-xxx.md`.

## Design

- `current-status.md` is rewritten as the latest snapshot and kept under 60 lines.
- `task-board.md` stores only index fields: status, priority, owner role, spec path, task status path, assignment path, dependencies, blockers, and next action.
- Every active task links to `.claw/tasks/TASK-xxx.md` through `task_status_path`.
- `.claw/tasks/TASK-xxx.md` stores progress, changed files, verification evidence, blockers, and handoff notes for one task only.
- Feature requirements and durable design stay in `docs/specs/`.
- Validation rejects hot-file history sections, oversized task cards, missing active task status files, and oversized per-task status files.

## Acceptance Criteria

- Protocol docs define progressive disclosure and line budgets.
- Templates start new projects in compact index mode.
- Current repository tasks are migrated into separate `.claw/tasks/TASK-xxx.md` files.
- `scripts/validate-state.py .claw` passes after migration.
- Python syntax checks pass for updated scripts.

## Verification

- `python3 scripts/validate-state.py .claw`
- `PYTHONPYCACHEPREFIX=/private/tmp/cc-aidev-pycache python3 -m py_compile scripts/validate-state.py`
