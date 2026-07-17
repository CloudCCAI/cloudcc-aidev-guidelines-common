---
kind: feature-spec
feature_id: FEAT-010
title: Progressive state indexing
status: implemented
owner_role: shared
task_ids: TASK-010
related_decisions: ADR-010
related_issues: none
updated_at: 2026-05-27T08:10:43Z
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
- In async manager-gated delivery, `.claw/tasks/TASK-xxx.md` is the developer-writable source for routine contribution progress. `task-board.md` is a manager/integration coordination index and can lag briefly unless assignment scope explicitly authorizes the developer to edit board fields.
- Feature requirements and durable design stay in `docs/specs/`.
- Validation rejects hot-file history sections, oversized task cards, missing active task status files, and oversized per-task status files.

## Acceptance Criteria

- Protocol docs define progressive disclosure and line budgets.
- Templates start new projects in compact index mode.
- Current repository tasks are migrated into separate `.claw/tasks/TASK-xxx.md` files.
- Async manager-gated docs explain that developer progress updates do not require `task-board.md` write scope.
- `skill/scripts/validate-state.py .claw` passes after migration.
- Python syntax checks pass for updated scripts.

## Verification

- `python3 skill/scripts/validate-state.py .claw`
- `git diff --check`
