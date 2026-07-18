---
kind: task-status
schema_version: 5
task_id: TASK-bimo-004
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

# TASK-bimo-004 - 动态校验与兼容

## Current State

- Status: `done`
- Spec: `docs/specs/FEAT-bimo-001-guided-project-management-lifecycle.md`
- Assignment: none
- Next action: none.

## Scope

- Preserve validation for v4 projects without a manifest.
- Dynamically require only enabled core/module and triggered event files in v5.
- Validate file init states, new naming, legacy index, cross references, and secrets.
- Use `.claw` as the only supported state directory.

## Progress

- Implemented v4 fallback and manifest/catalog-driven v5 validation with mode-, module-, lifecycle-, and event-aware requirements.
- Added manifest and legacy-index schemas, core completion/sentinel checks, module semantic validation, new/legacy naming checks, cross-reference gates, and secret restrictions.
- Disabled modules are not loaded; grandfathered block-mapping indexes and pending project-mode checkpoints are valid in their intended phases.

## Verification

- Status: `passed`
- Evidence: complete validator suite plus root v4, both v5 fixtures, legacy fixture, JSON schema syntax, and negative policy tests passed.

## Handoff

- Complete. Continue using the explicit immutable index rather than Git timestamps.
