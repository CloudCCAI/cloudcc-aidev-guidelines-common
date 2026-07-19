---
kind: task-status
schema_version: 5
task_id: TASK-bimo-008
task_type: feature
feature_id: FEAT-bimo-004
policy_version: 3
created_at: 2026-07-19T01:15:45Z
created_by: "Bimo"
created_by_slug: bimo
created_by_source: global_git_config_user_name
created_by_developer_id: none
assignee: bimo
owner_slug: bimo
owner_role: shared
status: done
stage: verification
branch: n/a
assignment_path: none
change_request_url: n/a
pr_url: n/a
next_action: "none"
updated_at: 2026-07-19T01:26:47Z
updated_by: "ai"
---

# TASK-bimo-008 - Project Documentation Directories

## Current State

- Status: `done`
- Next action: none
- Blocked: none
- Feature: `FEAT-bimo-004`
- Assignment: none

## Progress

- User confirmed the help/manual and feature/flow design documentation responsibilities.
- `FEAT-bimo-004` approved; canonical lowercase paths selected for cross-platform compatibility.
- Added catalog-driven, localized, idempotent creation of `docs/help/README.md` and `docs/design/README.md` during start/adopt/sync.
- Added 5.0.2 validation, directory-map integration, examples, documentation, and non-overwrite recovery coverage.

## Changed Files

- Onboarding/validation scripts, state catalog, English/Chinese project-doc templates, directory-map templates, v5 examples, protocol references, and onboarding tests.

## Verification

- Status: `passed`
- Evidence: 79/79 unit tests passed; Python compile and shell syntax checks passed; strict Greenfield/Brownfield v5, legacy v4 fixture, and repository-state validation passed.

## Handoff

- Feature is verified and ready for release review.
