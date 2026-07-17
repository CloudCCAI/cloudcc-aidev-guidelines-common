---
kind: task-status
task_id: TASK-011
assignee: unassigned
owner_role: shared
status: review
branch: main
change_request_url: n/a
pr_url: n/a
updated_at: 2026-07-17T06:55:02Z
updated_by: codex
---

# TASK-011 - Separate the skill package

## Current State

- Status: `review`
- Next action: user review the skill package layout
- Blocked: none
- Spec: `docs/specs/FEAT-011-skill-package-layout.md`
- Assignment: none

## Progress

- Confirmed that the skill scripts use paths relative to the skill root.
- Confirmed that the hard identity gate is not enabled in this repository.
- Moved the complete distributable package into `skill/`.
- Updated project paths, install source, release checks, current specs, and project state references.
- Updated the bundled sample project to the current progressive state model.
- Moved the canonical version marker to `metadata.skill_version` for standard skill compatibility.

## Changed Files

- `skill/` package contents
- `README.md`, `AGENTS.md`, `RELEASE_TEMPLATE.md`
- `.claw/` project state
- `docs/specs/`

## Verification

- Status: `passed`
- Evidence: standard skill validation; project, sample, and temporary-project state validation; Python and Shell syntax checks; CLI help checks; layout assertions; `git diff --check`

## Handoff

- Keep the repository root focused on project development and `skill/` focused on distributable skill content.
