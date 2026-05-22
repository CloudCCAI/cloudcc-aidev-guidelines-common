---
kind: task-status
task_id: TASK-008
assignee: unassigned
owner_role: shared
status: review
branch: n/a
change_request_url: n/a
pr_url: n/a
updated_at: 2026-05-22T00:00:00Z
updated_by: codex
---

# TASK-008 - Task Status

## Current State

- Status: `review`
- Next action: commit and push release `4.1.1` to Codeup `origin` and GitHub `github`
- Blocked: none
- Spec: `docs/specs/FEAT-008-codeup-change-request-submission.md`
- Assignment: none

## Progress

- Codeup change request creation and local Yunxiao token storage helpers are implemented.
- `CreateChangeRequest` now treats `repositoryId` as the path parameter and always sends numeric `sourceProjectId` and `targetProjectId` in the JSON body.
- Current repository local ignored defaults were resolved from Codeup `ListRepositories` and written to `.claw-local/codeup.env` with repository/project id `6551067`.
- Release version is `4.1.1` because Codeup `origin/main` already contained `4.1.0`.

## Changed Files

- `scripts/create-codeup-change-request.py`
- `SKILL.md`, `README.md`, `STATE-MODEL.md`, `CHANGELOG.md`
- `templates/platforms/codeup/README.md`
- `docs/specs/FEAT-008-codeup-change-request-submission.md`
- `.claw/current-status.md`, `.claw/task-board.md`, `.claw/test-report.md`, `.claw/tasks/TASK-008.md`

## Verification

- Status: `passed`
- Evidence: Codeup repository lookup for `6551067`; local config dry-run; Python syntax; state validation; diff whitespace

## Handoff

- Token material must stay in environment variables or `.claw-local/`, never tracked project state.
- Do not downgrade the skill below `4.1.0`; future Codeup fixes should continue from `4.1.1` or later.
