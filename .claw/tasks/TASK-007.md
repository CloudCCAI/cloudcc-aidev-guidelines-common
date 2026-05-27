---
kind: task-status
task_id: TASK-007
assignee: unassigned
owner_role: shared
status: review
branch: n/a
change_request_url: n/a
pr_url: n/a
updated_at: 2026-05-27T09:21:22Z
updated_by: codex
---

# TASK-007 - Task Status

## Current State

- Status: `review`
- Next action: release 4.1.3
- Blocked: none
- Spec: `docs/specs/FEAT-007-task-bounded-broad-code-authorization.md`
- Assignment: none

## Progress

- Task-bounded broad code authorization is implemented while preserving exact-file mode for narrow tasks.
- Fixed `scripts/check-assignment.py` for release `4.1.3` so `allowed_write_roots: frontend/src` authorizes files under `frontend/src/...` without requiring PMs to write `frontend/src/**`.
- Preserved exact `scope_files` semantics and verified bare `protected_paths` still block recursively.

## Changed Files

- `scripts/check-assignment.py`, `SKILL.md`, `STATE-MODEL.md`, `README.md`, `templates/parallel/assignment.yaml`, `templates/parallel/developer.yaml`, `docs/specs/FEAT-007-task-bounded-broad-code-authorization.md`, `CHANGELOG.md`

## Verification

- Status: `passed`
- Evidence: temporary assignment fixture for `allowed_write_roots: frontend/src`; exact `scope_files` negative check; protected-path negative check; `py_compile`; `python3 scripts/validate-state.py .claw`; `git diff --check`

## Handoff

- Future PRs should explain cross-module changes through a change manifest rather than narrowing all code paths up front. PMs may write directory roots as `frontend/src`, `frontend/src/`, or `frontend/src/**`; use `scope_files` for exact file grants.
