---
kind: task-status
schema_version: 5
task_id: TASK-bimo-001
task_type: feature
feature_id: FEAT-bimo-001
policy_version: 2
created_at: 2026-07-18T02:05:46Z
created_by: Bimo
created_by_slug: bimo
created_by_source: git_config_user_name
created_by_developer_id: none
assignee: bimo
owner_slug: bimo
owner_role: shared
status: done
stage: complete
branch: main
assignment_path: none
next_action: none
updated_at: 2026-07-18T03:05:43Z
updated_by: Bimo
---

# TASK-bimo-001 - 初始化内核

## Current State

- Status: `done`
- Spec: `docs/specs/FEAT-bimo-001-guided-project-management-lifecycle.md`
- Assignment: none
- Next action: none.

## Scope

- `.claw`-only project preflight and Greenfield/Brownfield recommendation.
- Manifest-driven module switches and per-file initialization status.
- Guided, resumable onboarding with empty task board and no event-file precreation.
- Core templates including `ARCHITECTURE` and `directory-map.md`.

## Progress

- Implemented manifest/catalog routing, Greenfield/Brownfield evidence, module switches, resumable per-file onboarding, sentinel completion gates, finalization, and core templates.
- Finalization now regenerates an idle multi-task hot index and is idempotent.
- README/AGENTS guidance and `.claw-local/` ignore protection are installed non-destructively.

## Verification

- Status: `passed`
- Evidence: full 67-test suite, Greenfield/Brownfield fixtures, module-combination forward tests, and shell syntax checks passed.

## Handoff

- Complete. Preserve the documented non-destructive behavior in future changes.
